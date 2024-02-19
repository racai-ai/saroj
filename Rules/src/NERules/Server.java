package NERules;
import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import ro.racai.conllup.CONLLUPReader;
import ro.racai.conllup.CONLLUPWriter;
import rules.RulesProcessor;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.URLDecoder;
import java.io.InputStreamReader;

import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Paths;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * This class implements the server for RoAnonymizer
 * 
 *
 */
@SuppressWarnings("restriction")
public class Server {
    
	public static void help() {
		System.out.println("NERules.Server RULES PORT\n");
		System.out.println("RULES = json with rules");
		System.out.println("PORT = port for server process");
	}
	
    public static void main(String[] args) throws IOException {
    	Locale.setDefault(Locale.ENGLISH);
    	if(args.length!=2) {
    		help();
    		return ;
    	}
    	
    	String rulesJson=args[0];
    	int port=Integer.parseInt(args[1]);
    	
    	System.out.println("Loading rules from "+rulesJson);
    	RulesProcessor rp=new RulesProcessor(Paths.get(rulesJson));
    	
        System.out.println("Starting server on port "+port);
		HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1",port),0);
        server.createContext("/checkHealth", new CheckHealthHandler(null));
        server.createContext("/process", new ProcessHandler(null,rp));

        server.start();
    }
    
    public static HashMap<String,String> getRequestParams(InputStream input) throws IOException {
        HashMap<String,String> params=new HashMap<String,String>(10);
        Integer state=0;
        String separator=""; 
        String currentName="";
        String currentContent="";

        BufferedReader in=new BufferedReader(new InputStreamReader(input));
        for(String line=in.readLine();line!=null && state!=100;line=in.readLine()){
            switch(state){
            case 0:
                if(line.length()>0){
                    separator=line;
                    state=1;
                }
                break;
            case 1:
                if(line.startsWith("Content-Disposition: form-data")){
                    int pos=line.indexOf("name=\"");
                    if(pos>0){
                        currentName=line.substring(pos+6);
                        pos=currentName.indexOf('"');
                        if(pos>0){
                            currentName=currentName.substring(0,pos);
                            state=2;
                        }
                    }
                }
                break;
            case 2:
                if(line.length()==0)state=3;
                break;
            case 3:
                if(line.startsWith(separator)){
                    params.put(currentName, currentContent);
                    currentName="";
                    currentContent="";
                    state=1;
                    if(line.equals(separator+"--"))state=100;
                }else{
                    if(currentContent.length()>0)currentContent+="\n";
                    currentContent+=line;
                }
                break;
            }
            //stringBuilder.append(line + "\n");
        };
        in.close();
        
        return params;
    }
    
    public static Map<String, String> splitQuery(URI url) throws UnsupportedEncodingException {
        Map<String, String> query_pairs = new HashMap<String, String>();
        String query = url.getQuery();
        if(query!=null) {
	        String[] pairs = query.split("&");
	        for (String pair : pairs) {
	            int idx = pair.indexOf("=");
	            query_pairs.put(URLDecoder.decode(pair.substring(0, idx), "UTF-8"), URLDecoder.decode(pair.substring(idx + 1), "UTF-8"));
	        }
        }
        return query_pairs;
    }    

    static abstract class CoreHandler implements HttpHandler {
        public String base_log_path;
        
        public CoreHandler(String base_log_path){
            this.base_log_path=base_log_path;
        }
        
        public String escape(String s){
            s=s.replace("\n","\\n");
            s=s.replace("\"","'");
            return s;
        }
        
        public abstract String getResult(JSONObject jsonData, String jsonStr) throws Exception;
        
        @Override
        public void handle(HttpExchange ex) throws IOException {
            try{
            	Map<String,String> params=splitQuery(ex.getRequestURI());
            	HashMap<String,String> paramsPost=getRequestParams(ex.getRequestBody());
            	if(paramsPost!=null) {
            		for(Map.Entry<String, String> entry:paramsPost.entrySet()) {
            			params.put(entry.getKey(), entry.getValue());
            		}
            	}
            	
                String error=null;
                String result=null;

                if(!params.containsKey("input")) {
                	error="input key not found";
                }else {
                
	                try {
	                	String jsonStr=params.get("input");
	                	JSONObject jsonData=new JSONObject(jsonStr);
	                	
	                	result=getResult(jsonData,jsonStr);
	                }catch(Exception exRun) {
	                	error=String.format("Exception [%s]", exRun.getMessage());
	                	exRun.printStackTrace();
	                }

                }
                
                // DO LOGGING
                String ip=ex.getRemoteAddress().getAddress().toString();
                ip=ip.substring(ip.indexOf('/')+1);
                
                DateFormat dateFormat = new SimpleDateFormat("yyyy");
                Date date = new Date();
                String year=dateFormat.format(date);
                dateFormat = new SimpleDateFormat("MM");
                String month=dateFormat.format(date);
                dateFormat = new SimpleDateFormat("dd");
                String day=dateFormat.format(date);
                dateFormat=new SimpleDateFormat("HHmmss");
                String time=dateFormat.format(date);

                PrintStream outLog = System.out; 
                if(this.base_log_path!=null) {
                    String path=this.base_log_path+"/"+year+"/"+month;
                    File log_path=new File(path);
                    log_path.mkdirs();
                	outLog=new PrintStream(new FileOutputStream(path+"/"+day+".log",true),true,"UTF-8");
                }
                
                /*if(FULL_LOG) {
                	outLog.println(String.format("%s-%s-%s %s\t%s\t%s", year,month,day,time,ip,ex.getRequestURI().toString()));
	                Headers reqh=ex.getRequestHeaders();
	                for(Map.Entry<String,List<String>> entry:reqh.entrySet()){
	                    for(String s:entry.getValue()){
	                        outLog.println(entry.getKey()+":"+s);
	                    }
	                }
	                outLog.println("\n--------------------------------------------------------------------------------\n");
	                outLog.println("Request params:");
	                for(Map.Entry<String,String> entry:params.entrySet()) {
	                	outLog.println(entry.getKey()+"="+entry.getValue());
	                }
	                //outLog.println("\n--------------------------------------------------------------------------------\n");
	                //outLog.println("Response:");
	                //outLog.println(response);
                }else {*/
                	outLog.print(String.format("%s-%s-%s %s\t%s\t%s\t", year,month,day,time,ip,ex.getRequestURI().toString()));
	                boolean first=true;
                	for(Map.Entry<String,String> entry:params.entrySet()) {
                		if(first)first=false; else outLog.print("|");
	                	outLog.print(entry.getKey()+"="+entry.getValue());
	                }
                	outLog.println();
                /*}*/
                	
                if(this.base_log_path!=null) {outLog.close();}
                
                
                // SEND REPLY
                Headers headers=ex.getResponseHeaders();

                if(error!=null || result==null) {
                    headers.add("Content-type", "text/plain; charset=utf-8");

                    ByteArrayOutputStream baos=new ByteArrayOutputStream();
                	PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(baos,StandardCharsets.UTF_8)));

                	JSONObject obj = new JSONObject();
                	obj.put("status", "ERROR");
                	obj.put("message", error);
                	out.print(obj.toString());
                	out.close();

                	String response=new String(baos.toByteArray(),StandardCharsets.UTF_8);

                
                	ex.sendResponseHeaders(200, response.getBytes(StandardCharsets.UTF_8).length);
                
                	OutputStream os = ex.getResponseBody();
                	os.write(response.getBytes(StandardCharsets.UTF_8));
                	os.close();
                
                	ex.close();
                }else {
                    headers.add("Content-type", "text/plain");
                    byte[] resultBytes=result.getBytes();
                	ex.sendResponseHeaders(200, resultBytes.length);
                	OutputStream os = ex.getResponseBody();
                	os.write(resultBytes);
                	os.close();
                	ex.close();
                }
            }catch(Exception exception){
                System.out.println("Exception while handling request:");
                exception.printStackTrace();

                ex.sendResponseHeaders(500, 0);
                
                OutputStream os = ex.getResponseBody();
                os.close();

            }
                
        }
    }
    
    static class CheckHealthHandler extends CoreHandler {
		public CheckHealthHandler(String base_log_path) {
			super(base_log_path);
		}

		public String getResult(JSONObject jsonData, String jsonStr) throws JSONException, IOException {
			return "{\"status\":\"OK\", \"message\":\"\"}";
    	}
    }

    static class ProcessHandler extends CoreHandler {
    	RulesProcessor rp;
    	
		public ProcessHandler(String base_log_path, RulesProcessor rp) {
			super(base_log_path);
			this.rp=rp;
		}

		public String getResult(JSONObject jsonData, String jsonStr) throws JSONException, IOException {
			String input=jsonData.getString("input");
			String output=jsonData.getString("output");
			
			CONLLUPReader in=new CONLLUPReader(Paths.get(input));
			CONLLUPWriter out=new CONLLUPWriter(Paths.get(output), new ArrayList<String>(), new ArrayList<String>(), new ArrayList<String>());
			
			rp.processDocument(in, out);
			
			in.close();
			out.close();
			
			return "{\"status\":\"OK\", \"message\":\"\"}";
    	}
    }

    
}

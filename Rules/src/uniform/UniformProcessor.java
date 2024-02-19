package uniform;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;

import ro.racai.base.Sentence;
import ro.racai.base.Token;
import ro.racai.conllup.CONLLUPReader;
import ro.racai.conllup.CONLLUPWriter;

public class UniformProcessor {

	private HashMap<String,EntityType> entities=new HashMap<>();
	private int maxTokens=0;
	private int minw=0;
	
	public UniformProcessor(int minw) {
		this.minw=minw;
	}
	
	public String getTokenKey(Token t, String key1, String key2) {
		String s=t.getByKey(key1);
		if(s==null)s=t.getByKey(key2);
		return s;
	}
	
	public void addCurrentEntity(ArrayList<String> current, String type) {
		if(current.size()==0 || current.size()<minw)return ;
		
		if(current.size()>maxTokens)maxTokens=current.size();
		
		Collections.sort(current);
		String name=String.join(" ", current);
		if(entities.containsKey(name)) {
			entities.get(name).setType(type);
		}else {
			entities.put(name, new EntityType(type));
		}
	}
	
	public int match(LinkedList<Token> tokens) {
		ArrayList<String> current=new ArrayList<>(maxTokens);
		
		for(int sz=Math.min(maxTokens, tokens.size()); sz>=1; sz--) {
			current.clear();
			for(int i=0;i<sz;i++) {
				String form=getTokenKey(tokens.get(i),"FORM","1").toLowerCase();
				current.add(form);
			}
			Collections.sort(current);
			String name=String.join(" ", current);
			if(entities.containsKey(name)) {
				String type=entities.get(name).getType();

				String kname=null;
				for(int i=0;i<sz;i++) {
					Token t=tokens.get(i);
					if(kname==null) {
						kname="NER";
						String s=t.getByKey(kname);
						if(s==null) kname=""+(tokens.get(0).getNumAnnotations()-1);
					}
					t.setByKey(kname,type);
				}
				return sz;				
			}
		}
		
		return 0;
	}
	
	public void processDocument(CONLLUPReader in, CONLLUPWriter out) throws IOException {
		entities.clear();
		maxTokens=0;
		
		ArrayList <String> current=new ArrayList<>();
		String currentNer="O";
		
		// Identify existing entities
		for(Sentence s=in.readSentence(); s!=null; s=in.readSentence()) {
			current.clear();
			currentNer="O";
			
			for(Token t : s.getTokens()) {
				String ner=getTokenKey(t,"NER",""+(t.getNumAnnotations()-1));
				if(ner.contentEquals("O") || ner.contentEquals("_")) {
					if(current.size()>0) {
						addCurrentEntity(current,currentNer);
						current.clear();
						currentNer="O";
					}
				}else {
					String form=getTokenKey(t,"FORM","1").toLowerCase();
					if(ner.startsWith("B-") || ner.startsWith("I-"))ner=ner.substring(2);
					if(!ner.contentEquals(currentNer)) {
						addCurrentEntity(current,currentNer);
						current.clear();
						currentNer=ner;
					}
					current.add(form);
				}
			}
			
			addCurrentEntity(current,currentNer);
		}

		
		in.reopen();
		
		LinkedList<Token> tokens=new LinkedList<>();
		
		// Uniform
		for(Sentence s=in.readSentence(); s!=null; s=in.readSentence()) {
			
			for(Token t : s.getTokens()) {
				tokens.add(t);
				
				if(tokens.size()>maxTokens) {
					int n=this.match(tokens);
					if(n==0)tokens.removeFirst();
					else for(int i=0;i<n;i++)tokens.removeFirst();
				}
			}
			
			while(tokens.size()>0) {
				int n=this.match(tokens);
				if(n==0)tokens.removeFirst();
				else for(int i=0;i<n;i++)tokens.removeFirst();
			}
			
			String last="";
			for(Token t : s.getTokens()) {
				String kname="NER";
				String currents=t.getByKey(kname);
				if(currents==null) {
					kname=""+(t.getNumAnnotations()-1);
					currents=t.getByKey(kname);
				}
				if(!currents.contentEquals("O") && !currents.contentEquals("_")) {
					if(currents.startsWith("B-") || currents.startsWith("I-"))
						currents=currents.substring(2);
					String currentEnt=currents;
					if(currents.contentEquals(last))currents="I-"+currents;
					else currents="B-"+currents;
					t.setByKey(kname, currents);
					last=currentEnt;
				}else last="O";
			}
			
			out.writeSentence(s);
			
		}
		
		
	}

}

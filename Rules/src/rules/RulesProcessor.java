package rules;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import ro.racai.base.Sentence;
import ro.racai.base.Token;
import ro.racai.conllup.CONLLUPReader;
import ro.racai.conllup.CONLLUPWriter;

public class RulesProcessor {

	private ArrayList<Rule> rules;
	private HashMap<String,Rule> ruleMap;
	private int max_length;

	public String getTokenKey(Token t, String key1, String key2) {
		String s=t.getByKey(key1);
		if(s==null)s=t.getByKey(key2);
		return s;
	}
	
	public RulesProcessor(Path filename) throws JSONException, IOException {
		JSONObject json = new JSONObject(new String ( Files.readAllBytes(filename)));
		max_length=json.optInt("max_sequence_length",20);
		rules=new ArrayList<>();
		ruleMap=new HashMap<>();
		JSONArray arr=json.getJSONArray("rules");
		for(int i=0;i<arr.length();i++) {
			Rule r=new Rule(this,arr.getJSONObject(i));
			rules.add(r);
			ruleMap.put(r.getName(), r);
		}
	}
	
	private MatchResult match(Token[] tokens) {
		int numMatch=0;
		Rule matchRule=null;
		
		for(Rule r:rules) {
			int n=r.match(tokens, false);
			if(n>numMatch) {
				numMatch=n;
				matchRule=r;
			}
		}
		
		if(matchRule!=null) {
			return new MatchResult(numMatch,matchRule);
		}
		
		return null;
	}
	
	public void processDocument(CONLLUPReader in, CONLLUPWriter out) throws IOException {
		LinkedList<Token> tokens=new LinkedList<>();
		
		/*if(in.getColumns().size()==0) {
			Collections.addAll(in.getColumns(),
					"ID","FORM","LEMMA","UPOS","XPOS","FEATS","HEAD","DEPREL","DEPS","MISC","START","END","NER"
			);
		}
		
		out.setColumnsOrder(in.getColumns());*/
		
		for(Sentence s=in.readSentence(); s!=null; s=in.readSentence()) {
			for(Token t : s.getTokens()) {
				tokens.addLast(t);
				if(tokens.size()>=max_length) {
					MatchResult mr=match((Token[])tokens.toArray(new Token[] {}));
					if(mr==null)tokens.removeFirst();
					else {
						mr.matchRule.match((Token[])tokens.toArray(new Token[] {}), true);
						for(int i=0;i<mr.numMatch;i++)tokens.removeFirst();
					}
				}
			}
			while(tokens.size()>0) {
				MatchResult mr=match((Token[])tokens.toArray(new Token[] {}));
				if(mr==null)tokens.removeFirst();
				else {
					mr.matchRule.match((Token[])tokens.toArray(new Token[] {}), true);
					for(int i=0;i<mr.numMatch;i++)tokens.removeFirst();
				}
			}
			
			String last="";
			for(Token t : s.getTokens()) {
				String kname="NER";
				String current=t.getByKey(kname);
				if(current==null) {
					kname=""+(t.getNumAnnotations()-1);
					current=t.getByKey(kname);
				}
				if(!current.contentEquals("O") && !current.contentEquals("_")) {
					if(current.startsWith("B-") || current.startsWith("I-"))
						current=current.substring(2);
					String currentEnt=current;
					if(current.contentEquals(last))current="I-"+current;
					else current="B-"+current;
					t.setByKey(kname, current);
					last=currentEnt;
				}else last="O";
			}
			
			out.writeSentence(s);
		}		
	}
	
	private class MatchResult {
		int numMatch;
		Rule matchRule;

		public MatchResult(int numMatch, Rule matchRule) {
			this.numMatch=numMatch;
			this.matchRule=matchRule;
		}
	}
}

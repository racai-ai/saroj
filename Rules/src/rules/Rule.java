package rules;

import java.util.ArrayList;

import org.json.JSONArray;
import org.json.JSONObject;

import ro.racai.base.Token;

public class Rule {

	private String name;
	private ArrayList<RuleCond> conditions;
	private RulesProcessor rp;
	
	public Rule(RulesProcessor rp,JSONObject ob) {
		this.rp=rp;
		name=ob.optString("name","");
		conditions=new ArrayList<>();
		JSONArray arr=ob.getJSONArray("conditions");
		for(int i=0;i<arr.length();i++) {
			conditions.add(new RuleCond(rp,arr.getJSONObject(i)));
		}
	}
	
	public int match(Token[] tokens, boolean apply) {
		int currentToken=0;
		int currentCond=0;
		int currentMatch=0;
		for(;currentToken<tokens.length && currentCond<conditions.size();) {
			RuleCond cond=conditions.get(currentCond);
			if(cond.matches(tokens[currentToken],apply)) {
				currentToken++;
				currentMatch++;
				if(currentMatch>=cond.getMax()) {
					currentCond++;
					currentMatch=0;
				}
			}else {
				if(currentMatch>=cond.getMin()) {
					currentCond++;
					currentMatch=0;
				}else break;
			}
		}
		
		if(currentCond==conditions.size())return currentToken;
		
		if(currentToken<tokens.length) {
			for(;currentCond<conditions.size();currentCond++)
				if(conditions.get(currentCond).getMin()>0)return -1;
		}
		return currentToken;
	}

	public String getName() {
		return name;
	}
	
}

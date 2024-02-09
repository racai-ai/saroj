package rules;

import java.util.regex.Pattern;

import org.json.JSONObject;

import ro.racai.base.Token;

public class RuleCond {

	private Pattern form;
	private Pattern lemma;
	private Pattern ner;
	private String ann;
	private int formFirstLetter;
	private int formAllLetters;
	private int min;
	private int max;
	private RulesProcessor rp;
	
	public RuleCond(RulesProcessor rp, JSONObject ob) {
		this.rp=rp;
		form=null;
		if(ob.has("form")) {
			String formString=ob.getString("form");
			int flags=0;
			if(ob.optBoolean("formMatchCased", false)==false)flags=Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE;
			form=Pattern.compile(formString,flags);
		}
		
		lemma=null;
		if(ob.has("lemma")) {
			String lemmaString=ob.getString("lemma");
			int flags=0;
			if(ob.optBoolean("lemmaMatchCased", false)==false)flags=Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE;
			lemma=Pattern.compile(lemmaString,flags);
		}
		
		if(ob.has("ner")) {
			String nerString=ob.getString("ner");
			int flags=0;
			flags=Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE;
			ner=Pattern.compile(nerString,flags);
		}
		
		
		ann=ob.optString("ann", null);

		formFirstLetter=ob.optInt("formFirstLetter",0);
		formAllLetters=ob.optInt("formAllLetters",0);
		
		min=ob.optInt("min",1);
		max=ob.optInt("max",9999);
	}
	
	public boolean matches(Token t, boolean apply) {
		
		if(formFirstLetter!=0) {
			String s=t.getByKey("FORM");
			if(s==null)s=t.getByKey("1");
			if(formFirstLetter==1) { // uppercase
				if(!s.substring(0,1).contentEquals(s.substring(0,1).toUpperCase()))return false;
			}else if(formFirstLetter==2) {// lowercase
				if(!s.substring(0,1).contentEquals(s.substring(0,1).toLowerCase()))return false;
			}
		}
		
		if(formAllLetters!=0) {
			String s=t.getByKey("FORM");
			if(s==null)s=t.getByKey("1");
			if(formAllLetters==1) { // uppercase
				if(!s.contentEquals(s.toUpperCase()))return false;
			}else if(formFirstLetter==2) {// lowercase
				if(!s.substring(0,1).contentEquals(s.substring(0,1).toLowerCase()))return false;
			}
		}

		if(form!=null) {
			String s=t.getByKey("FORM");
			if(s==null)s=t.getByKey("1");
			if(!form.matcher(s).find())return false;
		}

		if(lemma!=null) {
			String s=t.getByKey("LEMMA");
			if(s==null)s=t.getByKey("2");
			if(!lemma.matcher(s).find())return false;
		}
		
		if(ner!=null) {
			String s=t.getByKey("NER");
			if(s==null)
				s=t.getByKey(""+(t.getNumAnnotations()-1));
			if(s.startsWith("B-") || s.startsWith("I-"))s=s.substring(2);
			else if(s.contentEquals("_"))s="O";
			
			if(!ner.matcher(s).find())return false;
		}
	
		if(apply) {
			if(ann!=null) {
				String kname="NER";
				String s=t.getByKey("NER");
				if(s==null)kname=""+(t.getNumAnnotations()-1);
				t.setByKey(kname, ann);
			}
		}
		
		return true;
	}

	public int getMin() {
		return min;
	}

	public int getMax() {
		return max;
	}
	
}

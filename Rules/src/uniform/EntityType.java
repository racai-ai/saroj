package uniform;

import java.util.HashMap;
import java.util.Map.Entry;

public class EntityType {

	public HashMap<String,Integer> type;

	public EntityType(String t) {
		type=new HashMap<>();
		type.put(t, Integer.valueOf(1));
	}
	
	public void setType(String t) {
		if(!type.containsKey(t))type.put(t, Integer.valueOf(1));
		else {
			type.put(t, Integer.valueOf(type.get(t)+1));
		}
	}
	
	public String getType() {
		String t=null;
		int n=0;
		for(Entry<String,Integer> ent:type.entrySet()) {
			if(ent.getValue()>n) {n=ent.getValue(); t=ent.getKey();}
		}
		return t;
	}
	
}

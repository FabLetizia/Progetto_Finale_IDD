package ruleBlockingGPT;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Map;

public class Main {
	public static void main(String[] args) throws FileNotFoundException, IOException {
		String[][] matrix = new Matrix().getMatrix();
		Clusterizator cl = new Clusterizator(matrix);
		
		Map<Integer, Integer> results = cl.getClustersFaster();
		for (Map.Entry<Integer, Integer> entry : results.entrySet()) {
            System.out.println("Record: " + entry.getKey() + ", Cluster: " + entry.getValue());
        }
		
	}
}

package ruleBlockingGPT;

import java.util.HashMap;
import java.util.Map;

public class Clusterizator {

	private String[][] matrix;
	private Map<Integer, Integer> record2cluster;

	public Clusterizator(String[][] matrix) {
		this.matrix = matrix;
		this.record2cluster = new HashMap<>();
	}

	/* PRIMO ALGORITMO PER I CONFRONTI (Faster) */
	// Strategia
		// Inizializzazione di "record2cluster": ad ogni Record (rappresentato dal suo indice di riga) è assegnato l'intero "0", che significa "da clusterizzare"
		// Si itera su tutte le righe della Matrice (una riga = un record nello Schema Mediato):
			// Se il record è "non-Clusterizzato" gli si assegna un Cluster -> chiamiamo questo record "record_i".
			// A questo punto si itera su tutte le righe a lui successive che sono "non-Clusterizzate" e si verifica la condizione booleana ("final_condition").
			// Se per il "record_j" la final_condition è rispettata, allora viene messo nello stesso Cluster di "record_i".
	
	/* L'Algoritmo è 'faster' perché ogni Record viene confrontato solo con i successivi: confronti dimezzati rispetto al caso "confronto ognuno con tutti".
	 * I confronti sono ulteriormente ridotti dal fatto di skippare sia i "record_j" che i "record_i" già clusterizzati.
	 * Un effetto collaterale di questo approccio sta nel fatto di avere molti cluster: i primi di dimensione molto grande, gli ultimi molto piccoli (potenzialmente costituiti anche da un solo record) -> possiamo fare meglio?
	 */
	
	public Map<Integer, Integer> getClustersFaster() {
		int label = 0;
		
		// Inizializzazione dei Cluster: all'inizio, ogni record è "non-Clusterizzato" (value=0)
		for (int i=0; i<this.matrix.length; i++) {
			this.record2cluster.put(i, label);
		}

		// Si itera su tutti i Record
		for (int i=0; i<this.matrix.length-1; i++) {
			
			// Se il "record_i" corrente non è stato già clusterizzato gli si assegna un'etichetta e si avviano i confronti con gli altri record
			if (this.record2cluster.get(i) == 0) {
				label++;
				this.record2cluster.put(i, label);
				String[] record_i = this.matrix[i];
				int label_i = this.record2cluster.get(i);
				
				// Si itera su tutti i record successivi a "record_i"...
				for (int j=i+1; j<this.matrix.length; j++) {
					// ...ma trascurando quelli già Clusterizzati!
					if (this.record2cluster.get(j) == 0) {
						String[] record_j = this.matrix[j];

						boolean condition_name = this.editDistance(record_i[0], record_j[0]) <= 5;
						boolean condition_location = (record_i[1].contains(record_j[1])) || (record_j[1].contains(record_i[1]));
						boolean condition_category = (record_i[4].contains(record_j[4])) || (record_j[4].contains(record_i[4]));
						boolean final_condition = condition_name && (condition_location || condition_category);
						
						if (final_condition == true) {
							// Se la final_condition è verificata, "record_i" e "record_j" devono stare nello stesso Cluster!
							this.record2cluster.put(j, label_i);
						}
					}
				}
			}
			
			if (i % 10000 == 0)
				System.out.println("Fine del Processamento del Record " + i);
		}

		return this.record2cluster;
	}
	
	/* SECONDO ALGORITMO PER I CONFRONTI */
	// Sostanzialmente identico al precedente...ma con la differenza che il "record_i" non viene skippato se è già Clusterizzato (ovvero, se ha value != 0).
	
	public Map<Integer, Integer> getClusters() {
		int label = 0;
		
		// Inizializzazione dei Cluster: all'inizio, ogni record è "non-Clusterizzato" (value=0)
		for (int i=0; i<this.matrix.length; i++) {
			this.record2cluster.put(i, label);
		}

		// Si itera su tutti i Record
		for (int i=0; i<this.matrix.length-1; i++) {
			if (this.record2cluster.get(i) == 0) {
				// Se il "record_i" corrente è "non-Clusterizzato", abbiamo identificato un nuovo Cluster (label++)
				label++;
				this.record2cluster.put(i, label);
			}
				// Viene comunque utilizzato per fare i confronti!
				// Supponiamo: 
					// - "matrix[0]" simile a "matrix[1]"
					// - "matrix[0]" non-simile a "matrix[2]"
					// - "matrix[1]" simile a "matrix[2]".
				// Con questa versione dell'Algoritmo, "matrix[0,1,2]" staranno nello stesso Cluster! Abbiamo quindi meno Cluster e di dimensione mediamente maggiore
				// ...e facciamo più confronti!
			
				String[] record_i = this.matrix[i];
				int label_i = this.record2cluster.get(i);
				
				for (int j=i+1; j<this.matrix.length; j++) {
					if (this.record2cluster.get(j) == 0) {
						String[] record_j = this.matrix[j];

						boolean condition_name = this.editDistance(record_i[0], record_j[0]) <= 5;
						boolean condition_location = (record_i[1].contains(record_j[1])) || (record_j[1].contains(record_i[1]));
						boolean condition_category = (record_i[4].contains(record_j[4])) || (record_j[4].contains(record_i[4]));
						boolean final_condition = condition_name && (condition_location || condition_category);
						if (final_condition == true) {
							this.record2cluster.put(j, label_i);
						}
					}
				}
				
			if (i % 10000 == 0)
				System.out.println("Fine del Processamento del Record " + i);
		}

		return this.record2cluster;
	}

	// Funzione per il Calcolo della Distanza di Levenshtein (o Edit Distance) tra due Stringhe
	private int editDistance(String str1, String str2) {
		int[][] dp = new int[str1.length() + 1][str2.length() + 1];

		for (int i = 0; i <= str1.length(); i++) {
			dp[i][0] = i;
		}

		for (int j = 0; j <= str2.length(); j++) {
			dp[0][j] = j;
		}

		for (int i = 1; i <= str1.length(); i++) {
			for (int j = 1; j <= str2.length(); j++) {
				if (str1.charAt(i - 1) == str2.charAt(j - 1)) {
					dp[i][j] = dp[i - 1][j - 1];
				} else {
					dp[i][j] = 1 + Math.min(Math.min(dp[i - 1][j], dp[i][j - 1]), dp[i - 1][j - 1]);
				}
			}
		}

		return dp[str1.length()][str2.length()];
	}
}
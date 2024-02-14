package ruleBlockingGPT;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

public class Matrix {

	private String[][] matrix;
	private String filePath;

	public Matrix() throws FileNotFoundException, IOException {
		this.filePath = "./../MediateSchemaSemicolon.csv";
		this.matrix = this.buildMatrix();
	}

	private String[][] buildMatrix() throws FileNotFoundException, IOException {
		String[][] matrix = new String[81706][6];

		try (FileReader fileReader = new FileReader(this.filePath);
				CSVParser csvParser = new CSVParser(fileReader, CSVFormat.DEFAULT.withDelimiter(';').withFirstRecordAsHeader())) {

			// Definizione della matrice per memorizzare i dati

			int row = 0;
			for (CSVRecord csvRecord : csvParser) {
				// Memorizzazione delle colonne nella matrice
				for (int col = 0; col < 6; col++) {
					matrix[row][col] = csvRecord.get(col);
				}
				row++;
			}

		}
		System.out.println("Dataset letto con successo!");
		return matrix;
	}

	public String[][] getMatrix() {
		return this.matrix;
	}
}

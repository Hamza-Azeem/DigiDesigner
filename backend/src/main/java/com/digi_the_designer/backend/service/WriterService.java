package com.digi_the_designer.backend.service;

import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;

@Service
public class WriterService {
    public String generateAd(String txt) {
        try {
            // Path to the Python script
            String pythonScriptPath = "D:\\study\\backend\\digi_the_writer\\digi_the_writer_modified.py";

            // Build the process to run the Python script with arguments
            ProcessBuilder processBuilder = new ProcessBuilder(
                    "python",
                    pythonScriptPath,
                    "--prompt", txt
            );

            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            // Capture the script's output
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            int exitCode = process.waitFor();
            if (exitCode == 0) {
                return output.toString();
            } else {
                return ("Error executing the Python script: " + output.toString());
            }

        } catch (Exception e) {
            e.printStackTrace();
            return ("Server error: " + e.getMessage());
        }
    }
}

package com.digi_the_designer.backend.service;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

@Service
public class DesignerService {

    public String addNumbers(int num1, int num2) {
        try {
            // Path to the Python script
            String pythonScriptPath = "D:\\study\\backend\\addNums.py";

            // Build the process to run the Python script with arguments
            ProcessBuilder processBuilder = new ProcessBuilder(
                    "python",
                    pythonScriptPath,
                    "--num1", String.valueOf(num1),
                    "--num2", String.valueOf(num2)
            );

            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            // Read the output of the script
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
                return (output.toString());
            }

        } catch (Exception e) {
            e.printStackTrace();
            return e.getMessage();
        }
    }

    public String generateImage(MultipartFile file, String userPrompt) throws IOException, InterruptedException {
        String uploadDir = "D:\\study\\backend\\images";
        File directory = new File(uploadDir);
        if (!directory.exists()) {
            directory.mkdirs();
        }

        String imgPath = uploadDir + File.separator + file.getOriginalFilename();
        File savedFile = new File(imgPath);
        file.transferTo(savedFile);

        try {
            // Path to the Python script
            String pythonScriptPath = "D:\\study\\backend\\digi_the_designer_modified1.py";

            // Build the process to run the Python script with arguments
            ProcessBuilder processBuilder = new ProcessBuilder(
                    "python",
                    pythonScriptPath,
                    imgPath,
                    userPrompt
            );

            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            // Read the output of the script
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            int exitCode = process.waitFor();
            if (exitCode == 0) {
                return "Image generated and saved at: " + output.toString();
            } else {
                return "Error executing the Python script: " + output.toString();
            }

        } catch (Exception e) {
            e.printStackTrace();
            return "Server error: " + e.getMessage();
        }
    }
}


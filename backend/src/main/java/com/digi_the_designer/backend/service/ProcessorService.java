package com.digi_the_designer.backend.service;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;

@Service
public class ProcessorService {

    public String processImg(MultipartFile file) throws IOException, InterruptedException {
        String inputDir = "D:\\study\\backend\\proccessing\\uploaded_image";
        String outputDir = "D:\\study\\backend\\proccessing\\processed_images";

        // Ensure directories exist
        Files.createDirectories(Paths.get(inputDir));
        Files.createDirectories(Paths.get(outputDir));

        // Save the uploaded file temporarily
        String inputPath = inputDir + "/" + file.getOriginalFilename();
        String outputPath = outputDir + "/resized_" + file.getOriginalFilename();
        file.transferTo(new File(inputPath));

        // Call Python script
        String pythonScriptPath = "D:\\study\\backend\\proccessing\\digi_image_resizing.py"; // Adjust script path
        ProcessBuilder processBuilder = new ProcessBuilder(
                "python", pythonScriptPath,
                "--input_path", inputPath,
                "--output_path", outputPath
        );

        processBuilder.redirectErrorStream(true);
        Process process = processBuilder.start();

        // Read the script's output
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder output = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            output.append(line).append("\n");
        }

        int exitCode = process.waitFor();
        if (exitCode == 0) {
            return "Image successfully resized. Processed image saved at: " + outputPath;
        } else {
            return "Error processing image: " + output.toString();
        }
    }
}

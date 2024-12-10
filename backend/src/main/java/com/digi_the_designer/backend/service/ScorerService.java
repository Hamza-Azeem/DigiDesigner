package com.digi_the_designer.backend.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.List;
import java.util.Map;

@Service
public class ScorerService {
    public Object scorer(String campaignName) {
        String facebookAccessToken = "EAALeT0CinCIBO4ZAZCOcUIAKvZBdPKZBqQUQZBDwtMICuGZCgsLRTIx9z5SzKVOOaRg9vaN2zYeMPfPjUZAjp1OVfVZCSEYhl1uMjyfnYI30NruR8TvkZBZAhGNxsmhtw5YZBLlp658nA3qZBaTxjgbkfcmFdjcLTnafq2VGPF6XfFcs8lACf2CjyoxgCMeUwJHgGZC1r";
        String dataPath = "D:\\study\\backend\\scoring\\Modified_camps1.xlsx"; // Model data path

        try {
            String pythonScriptPath = "D:\\study\\backend\\scoring\\scoring(final_1).py";

            // Run the Python script with arguments
            ProcessBuilder processBuilder = new ProcessBuilder(
                    "python",
                    pythonScriptPath,
                    "--access_token", facebookAccessToken,
                    "--campaign_name", campaignName,
                    "--model_data_path", dataPath
            );

            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            // Capture the Python script output
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            int exitCode = process.waitFor();
            ObjectMapper mapper = new ObjectMapper();

            if (exitCode == 0) {
                // Parse JSON output into a list of maps
                return mapper.readValue(output.toString(), new TypeReference<List<Map<String, Object>>>() {});
            } else {
                return Map.of("error", "Python script failed", "details", output.toString());
            }

        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", "Server error", "message", e.getMessage());
        }
    }
}


package com.digi_the_designer.backend.controller;

import com.digi_the_designer.backend.service.DesignerService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/designer")
@RequiredArgsConstructor
public class DesignerController {

    private final DesignerService designerService;

    @PostMapping("/generate-image")
    public String generateImage(
            @RequestParam("image") MultipartFile file,
            @RequestParam("userPrompt") String userPrompt
    ) throws IOException, InterruptedException {

        return designerService.generateImage(file, userPrompt);
    }


}

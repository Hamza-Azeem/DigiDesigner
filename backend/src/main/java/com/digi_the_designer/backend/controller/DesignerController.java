package com.digi_the_designer.backend.controller;

import com.digi_the_designer.backend.service.DesignerService;
import com.digi_the_designer.backend.service.ProcessorService;
import com.digi_the_designer.backend.service.ScorerService;
import com.digi_the_designer.backend.service.WriterService;
import lombok.AllArgsConstructor;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/digi")
@AllArgsConstructor
public class DesignerController {

    private final DesignerService designerService;
    private final WriterService writerService;
    private final ScorerService scorerService;
    private final ProcessorService processorService;

    @PostMapping("/generate-image")
    public String generateImage(
            @RequestParam("image") MultipartFile file,
            @RequestParam("userPrompt") String userPrompt
    ) throws IOException, InterruptedException {

        return designerService.generateImage(file, userPrompt);
    }
    @PostMapping("/generate-txt")
    public String generateTxt(
            @RequestBody String txt
    ){
        return writerService.generateAd(txt);
    }
    @PostMapping("/scorer")
    public Object scorer(@RequestParam String txt){
        return scorerService.scorer(txt);
    }
    @PostMapping("/process-img")
    public String processImg(@RequestParam MultipartFile img) throws IOException, InterruptedException {
        return processorService.processImg(img);
    }


}

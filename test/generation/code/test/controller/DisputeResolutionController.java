package generation.code.test.controller;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import generation.code.test.service.DisputeResolutionService;
import java.util.Map;
import generation.code.test.service.DisputeResolutionService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import generation.code.test.service.DisputeResolutionService;
import java.util.Map;

package generation.code.test;

@RestController
@RequestMapping("/dispute")
public class DisputeResolutionController {
    private final DisputeResolutionService disputeResolutionService;

    public DisputeResolutionController(DisputeResolutionService disputeResolutionService) {
        this.disputeResolutionService = disputeResolutionService;
    }

    @PostMapping("/resolve")
    public ResponseEntity<Map<String, String>> resolveDispute(
            @RequestParam Long adminId,
            @RequestParam Long disputeId,
            @RequestParam String resolution) {
        Map<String, String> response = disputeResolutionService.resolveDispute(adminId, disputeId, resolution);
        return ResponseEntity.ok(response);
    }
}
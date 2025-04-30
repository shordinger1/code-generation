package generation.code.test.controller;
import generation.code.test.service.SellerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import generation.code.test.service.SellerService;

package generation.code.test.controller;

import generation.code.test.service.SellerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/sellers")
public class SellerController {

    @Autowired
    private SellerService sellerService;

    @PostMapping("/send-message")
    public ResponseEntity<Map<String, String>> sendBuyerMessage(
            @RequestParam Long sellerId,
            @RequestParam Long buyerId,
            @RequestParam String message) {
        Map<String, String> response = sellerService.sendMessageToBuyer(sellerId, buyerId, message);
        return ResponseEntity.ok(response);
    }
}
package generation.code.test.controller;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;
import generation.code.test.service.PaymentService;

package generation.code.test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    @Autowired
    private PaymentService paymentService;

    @PostMapping("/makePayment")
    public ResponseEntity<Map<String, String>> makePayment(@RequestParam Integer orderId, @RequestParam String paymentMethod) {
        Map<String, String> response = paymentService.processPayment(orderId, paymentMethod);
        return ResponseEntity.ok(response);
    }
}
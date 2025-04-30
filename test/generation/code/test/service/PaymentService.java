package generation.code.test.service;
import lombok.Data;
import java.util.HashMap;
import java.util.Map;
import generation.code.test.model.Order;

package generation.code.test;

import lombok.Data;
import java.util.HashMap;
import java.util.Map;

@Data
public class PaymentService {

    public Map<String, String> processPayment(Integer orderId, String paymentMethod) {
        Map<String, String> response = new HashMap<>();
        // Here you would add your business logic for processing the payment
        // For the sake of this example, let's assume the payment is always successful
        response.put("status", "success");
        response.put("orderId", orderId.toString());
        response.put("paymentMethod", paymentMethod);
        response.put("message", "Payment processed successfully.");
        return response;
    }
}
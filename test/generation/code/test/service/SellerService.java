package generation.code.test.service;
import lombok.Data;
import java.util.HashMap;
import java.util.Map;
import generation.code.test.model.Buyer;

package generation.code.test;

import lombok.Data;
import java.util.HashMap;
import java.util.Map;

@Data
public class SellerService {

    public Map<String, String> sendMessageToBuyer(Long sellerId, Long buyerId, String message) {
        Map<String, String> response = new HashMap<>();
        // Business logic for sending a message to the buyer
        // For now, we will simulate the response as success
        response.put("status", "success");
        response.put("message", "Message sent to buyer successfully.");
        return response;
    }
}
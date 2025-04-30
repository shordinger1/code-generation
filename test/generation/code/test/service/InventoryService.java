package generation.code.test.service;
import lombok.Data;
import java.util.HashMap;
import java.util.Map;
import generation.code.test.model.Product;
import generation.code.test.model.Seller;

package generation.code.test;

import lombok.Data;
import java.util.HashMap;
import java.util.Map;

@Data
public class InventoryService {

    public Map<String, String> updateInventory(Long seller_id, Long product_id, Integer new_stock) {
        Map<String, String> response = new HashMap<>();

        // This is a stubbed implementation. In a real application, you would perform the following steps:
        // - Validate the inputs
        // - Check if the seller and product exist
        // - Update the product stock in the database or repository

        // For demonstration purposes, let's assume the operation was successful:
        response.put("message", "Inventory updated successfully.");
        response.put("product_id", String.valueOf(product_id));
        response.put("new_stock", String.valueOf(new_stock));

        return response;
    }
}
package generation.code.test.controller;
import generation.code.test.InventoryService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import generation.code.test.service.InventoryService;

package generation.code.test.controller;

import generation.code.test.InventoryService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/inventory")
public class InventoryController {

    private final InventoryService inventoryService;

    public InventoryController(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }

    @PostMapping("/update")
    public ResponseEntity<Map<String, String>> updateInventory(@RequestBody Map<String, Object> request) {
        Long sellerId = ((Number) request.get("seller_id")).longValue();
        Long productId = ((Number) request.get("product_id")).longValue();
        Integer newStock = ((Number) request.get("new_stock")).intValue();

        Map<String, String> response = inventoryService.updateInventory(sellerId, productId, newStock);
        return ResponseEntity.ok(response);
    }
}
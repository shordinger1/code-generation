package generation.code.test.model;
import lombok.Data;
import generation.code.test.model.Seller;
import lombok.Data;


@Data
package generation.code.test;

import lombok.Data;

@Data
public class Product {
    private String id;
    private String name;
    private String description;
    private String price;
    private String stock;
    private String sellerId;
    private String images;
    private String category;
    private String tags;

    public Product(String id, String name, String description, String price,
                   String stock, String sellerId, String images,
                   String category, String tags) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.price = price;
        this.stock = stock;
        this.sellerId = sellerId;
        this.images = images;
        this.category = category;
        this.tags = tags;
    }
}
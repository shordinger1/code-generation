package generation.code.test.model;
import lombok.Data;
import generation.code.test.model.Buyer;
import generation.code.test.model.Seller;
import lombok.Data;


@Data
package generation.code.test;

import lombok.Data;

@Data
public class Order {
    private String id;
    private String buyerId;
    private String sellerId;
    private String orderDate;
    private String status;
    private String totalAmount;
    private String shippingAddress;
    private String paymentStatus;

    public Order(String id, String buyerId, String sellerId, String orderDate, String status, String totalAmount, String shippingAddress, String paymentStatus) {
        this.id = id;
        this.buyerId = buyerId;
        this.sellerId = sellerId;
        this.orderDate = orderDate;
        this.status = status;
        this.totalAmount = totalAmount;
        this.shippingAddress = shippingAddress;
        this.paymentStatus = paymentStatus;
    }
}
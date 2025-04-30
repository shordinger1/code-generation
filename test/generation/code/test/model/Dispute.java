package generation.code.test.model;
import lombok.Data;
import java.time.LocalDateTime;
import generation.code.test.model.Buyer;
import generation.code.test.model.Seller;
import lombok.Data;


@Data
package generation.code.test;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class Dispute {
    private Long disputeId;
    private Long buyerId;
    private Long sellerId;
    private String status;
    private String description;
    private LocalDateTime createdDate;

    public Dispute(Long disputeId, Long buyerId, Long sellerId, String status, String description, LocalDateTime createdDate) {
        this.disputeId = disputeId;
        this.buyerId = buyerId;
        this.sellerId = sellerId;
        this.status = status;
        this.description = description;
        this.createdDate = createdDate;
    }

    public static Dispute createDispute(Long disputeId, Long buyerId, Long sellerId, String status, String description) {
        LocalDateTime createdDate = LocalDateTime.now();
        return new Dispute(disputeId, buyerId, sellerId, status, description, createdDate);
    }

    public Dispute updateDisputeStatus(Long disputeId, String status) {
        this.disputeId = disputeId;
        this.status = status;
        return this;
    }

    public Dispute getDisputeDetails(Long disputeId) {
        // In a real application, you would retrieve the dispute details from a database.
        return this;
    }
}
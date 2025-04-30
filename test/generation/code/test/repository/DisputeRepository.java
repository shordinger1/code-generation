package generation.code.test.repository;
import java.util.Optional;
import java.util.List;
import lombok.Data;
import java.util.ArrayList;
import java.util.stream.Collectors;
import generation.code.test.model.Dispute;

package generation.code.test;

import java.util.Optional;
import java.util.List;
import lombok.Data;

@Data
public class DisputeRepository {
    // Sample data source: In real implementation, this could be a database or another source.
    private List<Dispute> disputeDatabase;

    public DisputeRepository() {
        this.disputeDatabase = new ArrayList<>(); // Initialize with an empty list
    }

    public Optional<Dispute> findDisputeById(Long disputeId) {
        return disputeDatabase.stream()
            .filter(dispute -> dispute.getDisputeId().equals(disputeId))
            .findFirst();
    }

    public List<Dispute> findDisputesByStatus(String status) {
        return disputeDatabase.stream()
            .filter(dispute -> dispute.getStatus().equals(status))
            .collect(Collectors.toList());
    }
}
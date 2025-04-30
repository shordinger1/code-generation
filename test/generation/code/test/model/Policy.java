package generation.code.test.model;

import lombok.Data;


@Data
public class Policy {
    private String policyName;
    private String policyContent;
    private Boolean isActive;

    public Policy(String policyName, String policyContent, Boolean isActive) {
        this.policyName = policyName;
        this.policyContent = policyContent;
        this.isActive = isActive;
    }

    public String getPolicyName() {
        return policyName;
    }

    public void setPolicyName(String policyName) {
        this.policyName = policyName;
    }

    public String getPolicyContent() {
        return policyContent;
    }

    public void setPolicyContent(String policyContent) {
        this.policyContent = policyContent;
    }

    public Boolean getIsActive() {
        return isActive;
    }

    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }
}
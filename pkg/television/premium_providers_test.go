package television

import (
	"encoding/base64"
	"encoding/json"
	"testing"
)

func TestExtractPremiumProvidersByProviderID(t *testing.T) {
	plansResponse := PlansResponse{
		Result: PlansResult{
			Plans: []Plan{
				{
					Providers: []PlanProvider{
						{ProviderID: "Z0177", ProviderName: "FanCode"},
					},
				},
				{
					Providers: []PlanProvider{
						{ProviderID: "Z0177", ProviderName: "FanCode"},
						{ProviderID: "Z0999", ProviderName: "Some Other Provider"},
					},
				},
			},
		},
	}

	premiumProviders := extractPremiumProviders(plansResponse)
	if len(premiumProviders) != 1 {
		t.Fatalf("expected 1 premium provider, got %d", len(premiumProviders))
	}

	if premiumProviders[0].ID != "Z0177" {
		t.Fatalf("expected provider ID Z0177, got %s", premiumProviders[0].ID)
	}
	if premiumProviders[0].ProviderID != "Z0177" {
		t.Fatalf("expected canonical provider ID Z0177, got %s", premiumProviders[0].ProviderID)
	}
	if premiumProviders[0].URL != "https://www.fancode.com/" {
		t.Fatalf("expected FanCode URL, got %s", premiumProviders[0].URL)
	}
}

func TestExtractPremiumProvidersByProviderName(t *testing.T) {
	plansResponse := PlansResponse{
		Result: PlansResult{
			Plans: []Plan{
				{
					Providers: []PlanProvider{
						{ProviderID: "", ProviderName: "JioCinema Premium"},
					},
				},
			},
		},
	}

	premiumProviders := extractPremiumProviders(plansResponse)
	if len(premiumProviders) != 1 {
		t.Fatalf("expected 1 premium provider, got %d", len(premiumProviders))
	}

	if premiumProviders[0].Name != "JioCinema Premium" {
		t.Fatalf("expected provider name JioCinema Premium, got %s", premiumProviders[0].Name)
	}
	if premiumProviders[0].URL != "https://www.jiocinema.com/" {
		t.Fatalf("expected JioCinema URL, got %s", premiumProviders[0].URL)
	}
}

func TestExtractPremiumProvidersFromAccessToken(t *testing.T) {
	claims := map[string]interface{}{
		"data": map[string]interface{}{
			"extra": "{\"plandetails\":{\"PackageInfo\":[{\"planid\":\"1019037\"},{\"planid\":\"1\"}]}}",
		},
	}

	payload, err := json.Marshal(claims)
	if err != nil {
		t.Fatalf("failed to marshal claims: %v", err)
	}

	accessToken := "header." + base64.RawURLEncoding.EncodeToString(payload) + ".signature"
	premiumProviders := extractPremiumProvidersFromAccessToken(accessToken)

	if len(premiumProviders) != 1 {
		t.Fatalf("expected 1 premium provider from token, got %d", len(premiumProviders))
	}
	if premiumProviders[0].Name != "FanCode" {
		t.Fatalf("expected FanCode from token, got %s", premiumProviders[0].Name)
	}
	if premiumProviders[0].ProviderID != "Z0177" {
		t.Fatalf("expected canonical provider ID Z0177 from token, got %s", premiumProviders[0].ProviderID)
	}
	if premiumProviders[0].URL != "https://www.fancode.com/" {
		t.Fatalf("expected FanCode URL from token, got %s", premiumProviders[0].URL)
	}
}

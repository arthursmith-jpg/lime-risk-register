from app import tag_notes

def test_rfp_tag():
    tags = tag_notes("RFP response submitted January 2026")
    assert "RFP / Tender" in tags

def test_escalation_tag():
    tags = tag_notes("GR dealing with significant escalation")
    assert "Active Escalation" in tags

def test_compliance_tag():
    tags = tag_notes("Increasing fines and impoundments issue persists.")
    assert "Compliance" in tags

def test_competition_tag():
    tags = tag_notes("Potential to benefit from decline in Dott scooter performance")
    assert "Competition" in tags

def test_data_sharing_tag():
    tags = tag_notes("Escalation ongoing due to data sharing as part of new contract")
    assert "Data Sharing" in tags

def test_contract_tag():
    tags = tag_notes("Contract Extension secured Feb 2026")
    assert "Contract / MOU" in tags

def test_political_risk_tag():
    tags = tag_notes("Cabinet Lead and Council opposed to any operations")
    assert "Political Risk" in tags

def test_fleet_tag():
    tags = tag_notes("uphill battle to get fleet increases")
    assert "Fleet / Deployment" in tags

def test_relationship_tag():
    tags = tag_notes("Difficult to build a 1-1 relationship with the city")
    assert "Relationship" in tags

def test_permit_tag():
    tags = tag_notes("Ongoing campaign to retain the permit, which is at risk")
    assert "Permit / License Risk" in tags

def test_multiple_tags():
    tags = tag_notes("Contract Extension secured. RFP/Tender likely in H2 2026")
    assert "Contract / MOU" in tags
    assert "RFP / Tender" in tags

def test_empty_notes():
    tags = tag_notes("")
    assert tags == []

def test_none_notes():
    tags = tag_notes(None)
    assert tags == []

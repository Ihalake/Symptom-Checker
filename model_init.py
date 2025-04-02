from transformers import BertTokenizer, BertForSequenceClassification
import torch

def load_model():
    model_name = "Lech-Iyoko/bert-symptom-checker"
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name)
    model.eval()  
    return model, tokenizer

LABEL_MAPPING = {
    0: "Sprains and Strains", 1: "Fractures", 2: "Contusions (Bruises)",
    3: "Cuts and Lacerations", 4: "Concussions", 5: "Burns", 6: "Dislocations",
    7: "Abrasions (Scrapes)", 8: "Whiplash Injuries", 9: "Eye Injuries", 10: "Puncture Wounds",
    11: "Bites and Stings", 12: "Back Injuries", 13: "Broken Nose", 14: "Knee Injuries",
    15: "Ankle Injuries", 16: "Shoulder Injuries", 17: "Wrist Injuries", 18: "Chest Injuries",
    19: "Head Injuries", 20: "Acne", 21: "Allergies", 22: "Alzheimer's Disease", 23: "Anemia",
    24: "Anxiety Disorders", 25: "Arthritis", 26: "Asthma", 27: "Back Pain", 28: "Bipolar Disorder",
    29: "Bronchitis", 30: "Cataracts", 31: "Chickenpox", 32: "COPD", 33: "Common Cold",
    34: "Conjunctivitis (Pink Eye)", 35: "Constipation", 36: "Coronary Heart Disease",
    37: "Depression", 38: "Diabetes Type 1", 39: "Diabetes Type 2", 40: "Diarrhea",
    41: "Ear Infections", 42: "Eczema", 43: "Fibromyalgia", 44: "Flu", 45: "GERD", 46: "Gout",
    47: "Hay Fever (Allergic Rhinitis)", 48: "Headaches", 49: "High Blood Pressure (Hypertension)",
    50: "High Cholesterol (Hypercholesterolemia)", 51: "IBS", 52: "Kidney Stones", 53: "Migraines",
    54: "Obesity", 55: "Osteoarthritis", 56: "Psoriasis", 57: "UTI", 58: "Pneumonia", 59: "Rheumatoid Arthritis", 60: "Schizophrenia",
}

def get_predictions(model, tokenizer, symptoms_text):
    inputs = tokenizer(symptoms_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.softmax(outputs.logits, dim=1)
    
    top_preds = predictions[0].topk(k=3)

    results = []
    for prob, idx in zip(top_preds.values, top_preds.indices):
        disease = LABEL_MAPPING[idx.item()]
        probability = round(prob.item() * 100, 2)
        results.append((disease, probability))
    
    return results
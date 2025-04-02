from transformers import pipeline

model = pipeline("text-classification", model="Lech-Iyoko/bert-symptom-checker")
result = model("I have a severe headache and nausea.")

# Format the result for natural language output
formatted_result = f"The predicted label is '{result[0]['label']}' with a confidence score of {result[0]['score']:.2f}."
print(formatted_result)

# Additional test case
result2 = model("I have a persistent cough and fever.")

# Format the additional test case result
formatted_result2 = f"The predicted label is '{result2[0]['label']}' with a confidence score of {result2[0]['score']:.2f}."
print(formatted_result2)
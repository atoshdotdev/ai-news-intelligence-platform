from gliner import GLiNER

MODEL_NAME = "urchade/gliner_medium-v2.1"


def extract_entities(
    model,
    text: str,
    labels: list[str],
    threshold: float = 0.5,
):
    return model.predict_entities(
        text,
        labels,
        threshold=threshold,
    )


def deduplicate_entities(entities):
    seen = {}

    for entity in entities:
        key = (entity["text"].lower(), entity["label"])

        if key not in seen:
            seen[key] = entity

    return list(seen.values())


def main():
    print("Loading GLiNER model...")

    model = GLiNER.from_pretrained(MODEL_NAME)

    article = """
    President Donald Trump, center, hosts a Cabinet meeting at Camp David on July 31, 2026.
President Donald Trump is not, historically, a Camp David guy.
The wood-wrapped rooms of the Laurel Lodge are not his happy place. His predecessors have chosen the retreat as an escape from cameras and formality; Trump rarely objects to having his picture taken or an extra chandelier or two.
There have been no reports of Trump ordering up new varnish on the rustic woodwork, no requests for his gold guy to apply a layer of gilt on the hand-carved wooden signs.
But there he was Friday, under the watchful gaze of his predecessors, convening his Cabinet amid the pines.
President Dwight D. Eisenhower, pictured recovering from a heart attack in 1955, was over his right shoulder as Trump warned about “gender mutilation of your children.”
On the far wall, a photo of President Gerald Ford discussing campaign strategy in 1976. Trump, at the table, was discussing an “invasion” of migrants in Spain.
Summoning his senior-most officials to the presidential redoubt at a moment of difficulty — without end, — Trump seemed to be looking for something different. He had originally scheduled the group trip in May but had to cancel when it rained.
The meeting, Trump announced as it began, would be “something very unique.”
And it was, at least for him. The White House’s cream-and-gold china service was replaced by bright red diner mugs. Instead of a black suburban, he was driven to camp in a golf cart.
Instead of asking everyone around his table to offer rave reviews of his tenure, he called only on a select few to deliver reports. The meeting did not stretch past three hours, as one at the White House did last year. He did not appear to doze off.
The red button Trump uses to summon a Diet Coke had made the trip to Maryland. And the glowing portrait he painted of his administration was unchanged.
Before reporters began asking questions, he largely avoided mention of the war, which has consumed his time and energy, often leaving him angry.
    """

    labels = [
        "person",
        "organization",
        "location",
        "country",
        "event",
        "date",
        "product",
        "money",
    ]

    entities = model.predict_entities(article, labels)

    entities = deduplicate_entities(entities)

    print("\nEntities found:\n")

    for entity in entities:
        print(f"{entity['text']} => {entity['label']} (score: {entity['score']:.3f})")


if __name__ == "__main__":
    main()

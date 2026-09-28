from pathlib import Path
import random
import pandas as pd


SEED = 42
random.seed(SEED)

OUTPUT_DIR = Path("data/mindcare_clean")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = [
    "crisis",
    "self_harm",
    "negated",
    "contextual",
    "neutral",
    "positive",
]


# -------------------------------------------------------------------
# Diverse phrase components.
# These are deliberately varied so the classifier cannot rely on
# one repeated sentence template.
# -------------------------------------------------------------------

OPENERS = [
    "Right now",
    "Today",
    "Lately",
    "This morning",
    "This evening",
    "Over the last few days",
    "Recently",
    "At the moment",
    "For the past week",
    "Since yesterday",
    "These days",
    "After everything that happened",
    "While dealing with everything",
    "When I think about everything",
]


SUPPORT_PHRASES = [
    "I need someone to listen",
    "I would like some support",
    "I am looking for help",
    "I want to talk about it",
    "I do not know who to talk to",
    "I am trying to explain how I feel",
    "I need a calm response",
    "I am hoping someone can understand",
]


# -------------------------------------------------------------------
# English examples
# -------------------------------------------------------------------

ENGLISH = {

    "crisis": [
        "I feel like I am at a breaking point.",
        "Everything feels completely overwhelming.",
        "I do not feel safe being alone with my thoughts.",
        "I feel like I cannot cope with what is happening.",
        "I am scared by how overwhelmed I feel.",
        "I feel unable to get through this moment on my own.",
        "My thoughts feel out of control right now.",
        "I feel like I am in an emotional crisis.",
        "I urgently need someone to help me through this.",
        "I am struggling to keep myself safe."
    ],

    "self_harm": [
        "I keep thinking about hurting myself.",
        "I have been having thoughts about self-harm.",
        "I am worried that I might hurt myself.",
        "The thoughts of harming myself keep returning.",
        "I feel an urge to hurt myself when I become overwhelmed.",
        "I am struggling with thoughts about self-injury.",
        "I have been thinking about hurting myself lately.",
        "I am afraid I may harm myself.",
        "Thoughts about self-harm are becoming difficult to ignore.",
        "I keep having unwanted thoughts about hurting myself."
    ],

    "negated": [
        "I am not thinking about hurting myself.",
        "I do not want to harm myself.",
        "I am not considering self-harm.",
        "I have no intention of hurting myself.",
        "I am safe and I am not thinking about self-harm.",
        "I do not have thoughts about harming myself.",
        "I am not suicidal.",
        "I am not in danger of hurting myself.",
        "I do not want to hurt myself.",
        "I am having a difficult day, but I am not thinking about self-harm."
    ],

    "contextual": [
        "My friend told me they are thinking about hurting themselves.",
        "Someone close to me has been talking about self-harm.",
        "My roommate is struggling and I want to support them.",
        "A family member says they do not feel safe.",
        "My friend is going through a serious emotional crisis.",
        "Someone I know has been having thoughts about self-harm.",
        "My classmate mentioned that they are struggling.",
        "I am worried about another person who seems overwhelmed.",
        "Someone close to me needs emotional support.",
        "My friend has been talking about very dark thoughts."
    ],

    "neutral": [
        "I have several assignments due this week.",
        "I am organizing my study schedule.",
        "I worked on my Python project today.",
        "I need to buy groceries tomorrow.",
        "I have a meeting in the morning.",
        "I am learning how to use GitHub.",
        "I spent the afternoon cleaning my room.",
        "I am planning my weekend.",
        "I watched a movie after class.",
        "I am preparing for an upcoming exam."
    ],

    "positive": [
        "I feel happy about how today went.",
        "I am proud of myself for finishing my work.",
        "I feel hopeful about the future.",
        "I had a really good conversation with my friend.",
        "I am excited about my new project.",
        "I feel calm and grateful today.",
        "I finally reached a goal I had been working toward.",
        "I feel motivated for tomorrow.",
        "Today gave me a lot of confidence.",
        "I feel supported by the people around me."
    ],
}


# -------------------------------------------------------------------
# Hinglish examples
# -------------------------------------------------------------------

HINGLISH = {

    "crisis": [
        "Mujhe lag raha hai ki main breaking point par hoon.",
        "Sab kuch bahut overwhelming lag raha hai.",
        "Mujhe abhi apne thoughts ke saath safe feel nahi ho raha.",
        "Mujhe lag raha hai main situation handle nahi kar paa raha.",
        "Main bahut zyada overwhelmed aur scared feel kar raha hoon.",
        "Mujhe lag raha hai main ye moment akela handle nahi kar sakta.",
        "Mere thoughts abhi control mein nahi lag rahe.",
        "Mujhe lag raha hai main emotional crisis mein hoon.",
        "Mujhe urgently kisi ki help chahiye.",
        "Mujhe khud ko safe rakhna difficult lag raha hai."
    ],

    "self_harm": [
        "Mere mind mein khud ko hurt karne ke thoughts aa rahe hain.",
        "Mujhe self-harm ke thoughts aa rahe hain.",
        "Mujhe darr hai ki main khud ko hurt kar sakta hoon.",
        "Khud ko harm karne ke thoughts baar baar aa rahe hain.",
        "Overwhelmed hone par mujhe khud ko hurt karne ka urge hota hai.",
        "Main self-injury ke thoughts se struggle kar raha hoon.",
        "Lately mujhe khud ko hurt karne ke thoughts aa rahe hain.",
        "Mujhe fear hai ki main khud ko harm kar sakta hoon.",
        "Self-harm ke thoughts ignore karna difficult ho raha hai.",
        "Mere mind mein khud ko hurt karne ke unwanted thoughts hain."
    ],

    "negated": [
        "Main khud ko hurt karne ke baare mein nahi soch raha hoon.",
        "Mujhe khud ko harm nahi karna hai.",
        "Main self-harm consider nahi kar raha hoon.",
        "Mera khud ko hurt karne ka koi intention nahi hai.",
        "Main safe hoon aur self-harm ke thoughts nahi aa rahe.",
        "Mere mind mein khud ko harm karne ke thoughts nahi hain.",
        "Main suicidal nahi hoon.",
        "Main khud ko hurt karne ke danger mein nahi hoon.",
        "Mujhe khud ko hurt nahi karna.",
        "Din difficult hai lekin self-harm ka thought nahi aa raha."
    ],

    "contextual": [
        "Mere friend ne bola ki woh khud ko hurt karne ke baare mein soch raha hai.",
        "Mera close person self-harm ki baat kar raha hai.",
        "Mera roommate struggle kar raha hai aur main usko support karna chahta hoon.",
        "Mere family member ne bola ki woh safe feel nahi kar raha.",
        "Mera friend serious emotional crisis se guzar raha hai.",
        "Mera classmate self-harm ke thoughts ke baare mein bata raha tha.",
        "Main kisi aur person ke liye worried hoon.",
        "Mera friend bahut overwhelmed lag raha hai.",
        "Mere close person ko emotional support chahiye.",
        "Mera friend dark thoughts ke baare mein baat kar raha hai."
    ],

    "neutral": [
        "Mere is week kaafi assignments hain.",
        "Main apna study schedule bana raha hoon.",
        "Aaj Python project par kaam kiya.",
        "Kal groceries lene jaana hai.",
        "Kal morning mein meeting hai.",
        "Main GitHub seekh raha hoon.",
        "Aaj room clean kiya.",
        "Weekend ke plans bana raha hoon.",
        "Class ke baad movie dekhi.",
        "Upcoming exam ke liye prepare kar raha hoon."
    ],

    "positive": [
        "Aaj ka din achha gaya aur main happy feel kar raha hoon.",
        "Work finish karke mujhe proud feel ho raha hai.",
        "Future ko lekar hopeful feel kar raha hoon.",
        "Friend ke saath achhi conversation hui.",
        "New project ko lekar main excited hoon.",
        "Aaj calm aur grateful feel kar raha hoon.",
        "Maine ek important goal achieve kiya.",
        "Kal ke liye motivated feel kar raha hoon.",
        "Aaj mujhe kaafi confidence mila.",
        "Mujhe apne aas paas ke logon ka support milta hai."
    ],
}


def make_variant(base, category, language, index):

    opener = random.choice(OPENERS)

    # Use different constructions rather than simply appending
    # the same suffix repeatedly.
    patterns = [
        f"{opener}, {base.lower()}",
        f"{base} {random.choice(SUPPORT_PHRASES)}.",
        f"{opener} I want to say that {base.lower()}",
        f"I wanted to mention that {base.lower()}",
        f"I have been feeling this way because of several things. {base}",
        f"{base} I am trying to make sense of it.",
        f"{base} and I wanted to talk about it.",
        f"{opener}, honestly, {base.lower()}",
    ]

    text = random.choice(patterns)

    return text.strip()


def build_category(category, count=200):

    rows = []

    # Generate many candidates.
    candidates = set()

    banks = [
        ("en", ENGLISH[category]),
        ("hinglish", HINGLISH[category]),
    ]

    attempts = 0

    while len(candidates) < count and attempts < count * 100:

        language, bank = random.choice(banks)

        base = random.choice(bank)

        text = make_variant(
            base,
            category,
            language,
            attempts,
        )

        normalized = " ".join(
            text.lower().split()
        )

        if normalized not in candidates:

            candidates.add(normalized)

            rows.append({
                "message": text,
                "category": category,
                "risk_level": (
                    "high"
                    if category in {
                        "crisis",
                        "self_harm",
                    }
                    else (
                        "medium"
                        if category == "contextual"
                        else "low"
                    )
                ),
                "language": language,
                "source_type": "synthetic"
            })

        attempts += 1

    if len(rows) < count:
        raise RuntimeError(
            f"Could only generate "
            f"{len(rows)} unique messages for "
            f"{category}"
        )

    return rows


def main():

    all_rows = []

    for category in CATEGORIES:

        print(
            f"Generating {category}..."
        )

        all_rows.extend(
            build_category(
                category,
                200,
            )
        )

    # Final global deduplication.
    df = pd.DataFrame(all_rows)

    df["normalized_message"] = (
        df["message"]
        .str.lower()
        .str.replace(
            r"\s+",
            " ",
            regex=True,
        )
        .str.strip()
    )

    df = df.drop_duplicates(
        subset="normalized_message"
    )

    df = df.drop(
        columns=["normalized_message"]
    )

    if len(df) < 1200:

        raise RuntimeError(
            f"Only {len(df)} unique messages "
            "remain after deduplication."
        )

    # Keep exactly 200 per class.
    selected = []

    for category in CATEGORIES:

        subset = df[
            df["category"] == category
        ].sample(
            n=200,
            random_state=SEED,
        )

        selected.append(subset)

    df = pd.concat(
        selected,
        ignore_index=True,
    )

    # Shuffle before splitting.
    df = df.sample(
        frac=1,
        random_state=SEED,
    ).reset_index(
        drop=True
    )

    # IMPORTANT:
    # Assign split AFTER deduplication.
    # This prevents identical messages appearing
    # across train/validation/test.
    df["split"] = ""

    for category in CATEGORIES:

        indices = df.index[
            df["category"] == category
        ].tolist()

        random.Random(
            SEED + CATEGORIES.index(category)
        ).shuffle(indices)

        train_indices = indices[:140]
        validation_indices = indices[140:170]
        test_indices = indices[170:200]

        df.loc[
            train_indices,
            "split"
        ] = "train"

        df.loc[
            validation_indices,
            "split"
        ] = "validation"

        df.loc[
            test_indices,
            "split"
        ] = "test"

    df.insert(
        0,
        "message_id",
        [
            f"MC-{i:04d}"
            for i in range(
                1,
                len(df) + 1,
            )
        ],
    )

    label_map = {
        category: i
        for i, category
        in enumerate(CATEGORIES)
    }

    df["label"] = df["category"].map(
        label_map
    )

    # Save complete dataset.
    df.to_csv(
        OUTPUT_DIR / "mindcare_clean_1200.csv",
        index=False,
    )

    # Save individual splits.
    df[
        df["split"] == "train"
    ].to_csv(
        OUTPUT_DIR / "train.csv",
        index=False,
    )

    df[
        df["split"] == "validation"
    ].to_csv(
        OUTPUT_DIR / "validation.csv",
        index=False,
    )

    df[
        df["split"] == "test"
    ].to_csv(
        OUTPUT_DIR / "test.csv",
        index=False,
    )

    print("\n" + "=" * 60)
    print("CLEAN DATASET CREATED")
    print("=" * 60)

    print(f"\nTotal: {len(df)}")

    print("\nCategories:")
    print(df["category"].value_counts())

    print("\nSplits:")
    print(df["split"].value_counts())

    print("\nExact duplicates:")
    print(
        df["message"].duplicated().sum()
    )

    print(
        "\nSaved to:",
        OUTPUT_DIR,
    )


if __name__ == "__main__":
    main()
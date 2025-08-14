import re
import sys
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os
import ast
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


def parse_log_file(filename):
    rows = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\[(.*?)\] UART: (\{.*\})", line)
            if not m:
                continue
            timestamp, payload = m.groups()
            try:
                data = ast.literal_eval(payload)
            except Exception:
                continue
            if data.get('type') == 'key':
                key = int(data.get('value', -1))
                rows.append({"timestamp": timestamp, "event": "key", "key": key})
            elif data.get('type') == 'proxy':
                dist = int(data.get('value', -1))
                rows.append({"timestamp": timestamp, "event": "proxy", "distance": dist})
            elif data.get('type') == 'volume':
                vol_key = str(data.get('key', 'none'))
                vol_val = int(data.get('value', 0))
                rows.append({"timestamp": timestamp, "event": "volume", "vol_key": vol_key, "vol_value": vol_val})
    return pd.DataFrame(rows)


def build_features(df):
    features = []
    last_key_time = None
    last_dist = 0
    last_vol_key = None
    last_vol_value = None
    for i, row in df.iterrows():
        if row["event"] == "proxy":
            last_dist = row["distance"]
        elif row["event"] == "volume":
            last_vol_key = row.get("vol_key", None)
            last_vol_value = row.get("vol_value", None)
        elif row["event"] == "key":
            t = pd.to_datetime(row["timestamp"])
            if last_key_time is not None:
                delta = (t - last_key_time).total_seconds()
            else:
                delta = 0
            last_key_time = t
            features.append({
                "key": row["key"],
                "delta": delta,
                "distance": last_dist,
                "vol_key": last_vol_key if last_vol_key is not None else "none",
                "vol_value": last_vol_value if last_vol_value is not None else 0
            })
    return pd.DataFrame(features)

def label_data(features_df, label):
    features_df["label"] = label
    return features_df


def train_model(labeled_df, model_path="ai_rf_model.pkl"):
    X = labeled_df[["key", "delta", "distance", "vol_value"]]
    y = labeled_df["label"]
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    joblib.dump(clf, model_path)
    print(f"[INFO] Model salvat în {model_path}")


def predict_on_log(logfile, model_path="ai_rf_model.pkl", n=20):
    df = parse_log_file(logfile)
    features = build_features(df)
    if len(features) < n:
        print("[WARN] Prea puține acțiuni pentru predicție!")
        return
    X = features[["key", "delta", "distance", "vol_value"]].tail(n)
    clf = joblib.load(model_path)
    preds = clf.predict(X)
    from collections import Counter
    c = Counter(preds)
    print(f"[PREDICT] Predicție pe ultimele {n} acțiuni: {c.most_common(1)[0][0]} ({c})")


def evaluate_model(labeled_df, model_path="ai_rf_model.pkl"):
    X = labeled_df[["key", "delta", "distance", "vol_value"]]
    y = labeled_df["label"]
    clf = joblib.load(model_path)
    y_pred = clf.predict(X)
    print("\n[STATISTICI] Classification report:\n", classification_report(y, y_pred))
    print("[STATISTICI] Accuracy:", accuracy_score(y, y_pred))
    cm = confusion_matrix(y, y_pred, labels=clf.classes_)
    plt.figure(figsize=(8,6))
    plt.imshow(cm, cmap='Blues')
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.xticks(range(len(clf.classes_)), clf.classes_, rotation=45)
    plt.yticks(range(len(clf.classes_)), clf.classes_)
    for i in range(len(clf.classes_)):
        for j in range(len(clf.classes_)):
            plt.text(j, i, cm[i, j], ha='center', va='center', color='red')
    plt.tight_layout()
    plt.show()

def accuracy_for_user(labeled_df, model_path, user):
    X = labeled_df[["key", "delta", "distance", "vol_value"]]
    y = labeled_df["label"]
    clf = joblib.load(model_path)
    y_pred = clf.predict(X)
    mask = (y == user)
    acc = (y_pred[mask] == user).mean()
    print(f"[ACCURACY] Acuratețea de recunoaștere pentru '{user}': {acc*100:.2f}% pe {mask.sum()} exemple.")

def prediction_distribution_for_user(labeled_df, model_path, user):
    X = labeled_df[["key", "delta", "distance", "vol_value"]]
    y = labeled_df["label"]
    clf = joblib.load(model_path)
    y_pred = clf.predict(X)
    from collections import Counter
    c = Counter(y_pred)
    print(f"[DISTRIBUTION] Predicții model pe toate datele:")
    for label, count in c.items():
        print(f"  {label}: {count} ({count/len(y_pred)*100:.2f}%)")
    print(f"[INFO] Din {len(y_pred)} exemple, modelul a prezis '{user}' de {c.get(user,0)} ori.")

def extract_features_to_csv(logfile, outfile):
    df = parse_log_file(logfile)
    features = build_features(df)
    features[["key", "delta", "distance", "vol_key", "vol_value"]].to_csv(outfile, index=False)
    print(f"[INFO] Features extrase în {outfile}")

def test_distribution_on_features(features_csv, model_path, user):
    df = pd.read_csv(features_csv)
    X = df[["key", "delta", "distance", "vol_value"]]
    clf = joblib.load(model_path)
    y_pred = clf.predict(X)
    from collections import Counter
    c = Counter(y_pred)
    print(f"[DISTRIBUTION-TEST] Predicții model pe datele de test:")
    for label, count in c.items():
        print(f"  {label}: {count} ({count/len(y_pred)*100:.2f}%)")
    print(f"[INFO] Din {len(y_pred)} exemple de test, modelul a prezis '{user}' de {c.get(user,0)} ori.")

def convert_to_binary_labels(infile, outfile, positive_label="IVASCU", negative_label="ALTII"):
    df = pd.read_csv(infile)
    df["label"] = df["label"].apply(lambda x: positive_label if x == positive_label else negative_label)
    df.to_csv(outfile, index=False)
    print(f"[INFO] Am salvat {outfile} cu etichete binare: {positive_label} / {negative_label}")

def train_test_split_and_stats(features_csv, label_col="label", test_size=0.2, random_state=42):
    df = pd.read_csv(features_csv)
    if label_col not in df.columns:
        print("[ERROR] Fișierul nu conține coloana de label!")
        return
    from sklearn.model_selection import train_test_split
    X = df[["key", "delta", "distance", "vol_value"]]
    y = df[label_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    from sklearn.metrics import classification_report, accuracy_score
    print("[TRAIN/TEST SPLIT] Classification report pe test:")
    print(classification_report(y_test, y_pred))
    print(f"[TRAIN/TEST SPLIT] Accuracy pe test: {accuracy_score(y_test, y_pred)*100:.2f}% ({sum(y_pred==y_test)}/{len(y_test)})")
    return clf, X_train, X_test, y_train, y_test, y_pred

if __name__ == "__main__":
    # python recunoastere_comportament.py label session_log.txt IVASCU
    # python recunoastere_comportament.py train labeled.csv
    # python recunoastere_comportament.py predict alt_session_log.txt

    if len(sys.argv) < 3:
        print("Usage:")
        print("  label <logfile> <user>")
        print("  train <labeled_csv>")
        print("  predict <logfile>")
        print("  stats <labeled_csv>")
        print("  acc <labeled_csv> <user>")
        print("  dist <labeled_csv> <user>")
        print("  extract <logfile> <outfile>")
        print("  disttest <features_csv> <user>")
        print("  binary <infile> <outfile>")
        print("  splitstats <labeled_csv>")
        sys.exit(1)

    # Always use the script's directory for labeled.csv and model
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    LABELED_PATH = os.path.join(BASEDIR, "labeled.csv")
    MODEL_PATH = os.path.join(BASEDIR, "ai_rf_model.pkl")

    cmd = sys.argv[1]
    if cmd == "label":
        logf = sys.argv[2]
        user = sys.argv[3]
        df = parse_log_file(logf)
        features = build_features(df)
        labeled = label_data(features, user)
        labeled.to_csv(LABELED_PATH, mode="a", header=not os.path.exists(LABELED_PATH), index=False)
        print(f"[INFO] Date etichetate adăugate pentru {user} în {LABELED_PATH}")
    elif cmd == "train":
        csvf = sys.argv[2]
        # Acceptă și calea relativă și absolută
        if not os.path.isabs(csvf):
            csvf = os.path.join(BASEDIR, csvf)
        df = pd.read_csv(csvf)
        train_model(df, model_path=MODEL_PATH)
    elif cmd == "predict":
        logf = sys.argv[2]
        predict_on_log(logf, model_path=MODEL_PATH)
    elif cmd == "stats":
        csvf = sys.argv[2]
        if not os.path.isabs(csvf):
            csvf = os.path.join(BASEDIR, csvf)
        df = pd.read_csv(csvf)
        evaluate_model(df, model_path=MODEL_PATH)
    elif cmd == "acc":
        csvf = sys.argv[2]
        user = sys.argv[3]
        if not os.path.isabs(csvf):
            csvf = os.path.join(BASEDIR, csvf)
        df = pd.read_csv(csvf)
        accuracy_for_user(df, model_path=MODEL_PATH, user=user)
    elif cmd == "dist":
        csvf = sys.argv[2]
        user = sys.argv[3]
        if not os.path.isabs(csvf):
            csvf = os.path.join(BASEDIR, csvf)
        df = pd.read_csv(csvf)
        prediction_distribution_for_user(df, model_path=MODEL_PATH, user=user)
    elif cmd == "extract":
        logf = sys.argv[2]
        outf = sys.argv[3]
        extract_features_to_csv(logf, outf)
    elif cmd == "disttest":
        features_csv = sys.argv[2]
        user = sys.argv[3]
        if not os.path.isabs(features_csv):
            features_csv = os.path.join(BASEDIR, features_csv)
        test_distribution_on_features(features_csv, model_path=MODEL_PATH, user=user)
    elif cmd == "binary":
        infile = sys.argv[2]
        outfile = sys.argv[3]
        convert_to_binary_labels(infile, outfile)
    elif cmd == "splitstats":
        features_csv = sys.argv[2]
        label_col = "label"
        if len(sys.argv) > 3:
            label_col = sys.argv[3]
        if not os.path.isabs(features_csv):
            features_csv = os.path.join(BASEDIR, features_csv)
        train_test_split_and_stats(features_csv, label_col=label_col)
    else:
        print("Comandă necunoscută.")

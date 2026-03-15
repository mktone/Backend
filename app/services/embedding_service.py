from sentence_transformers import SentenceTransformer, util

# 한국어 의미 유사도에 특화된 모델
MODEL_NAME = "jhgan/ko-sroberta-multitask"

# 유사 단어로 인정할 최소 유사도 (0~1)
SIMILARITY_THRESHOLD = 0.65


class EmbeddingService:
    def __init__(self):
        self._model: SentenceTransformer | None = None
        self._sign_words: list[str] = []
        self._embeddings = None

    def load_model(self) -> None:
        print("임베딩 모델 로딩 중...")
        self._model = SentenceTransformer(MODEL_NAME)
        print("임베딩 모델 로딩 완료")

    def build_index(self, sign_words: dict[str, list]) -> None:
        if self._model is None or not sign_words:
            return
        print(f"sign_db {len(sign_words)}개 단어 임베딩 계산 중...")
        self._sign_words = list(sign_words.keys())
        self._embeddings = self._model.encode(
            self._sign_words,
            convert_to_tensor=True,
            batch_size=256,
            show_progress_bar=True,
        )
        print("임베딩 인덱스 구축 완료")

    def find_similar(self, word: str) -> str | None:
        if self._model is None or self._embeddings is None or not self._sign_words:
            return None

        word_emb = self._model.encode(word, convert_to_tensor=True)
        cos_scores = util.cos_sim(word_emb, self._embeddings)[0]
        best_idx = int(cos_scores.argmax())

        if cos_scores[best_idx] >= SIMILARITY_THRESHOLD:
            return self._sign_words[best_idx]
        return None


embedding_service = EmbeddingService()

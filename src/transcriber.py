"""语音转写：阿里云 DashScope Paraformer，带说话人分离。

产出：按句划分、带说话人标签的转写文本（面试官 / 候选人）。
说话人分离是"AI 点评候选人答得如何"的前提——不区分说话人，
点评就无从谈起。

⚠️ 已知约束（写进 README 的选型分析里）：
录音文件识别要求音频可通过公网 URL 访问。本地文件需先上传到
OSS / 阿里云百炼临时存储，或改用实时识别接口流式读取本地文件（TODO）。
"""
from dataclasses import dataclass, field

from .config import ASR_MODEL, DASHSCOPE_API_KEY, ensure_api_key


@dataclass
class Utterance:
    speaker: str      # "interviewer" / "candidate" / "unknown"
    text: str
    begin_ms: int = 0
    end_ms: int = 0


@dataclass
class Transcript:
    utterances: list[Utterance] = field(default_factory=list)

    @property
    def dialogue(self) -> str:
        """拼成 "[interviewer] ...\\n[candidate] ..." 的对话文本，供下游 prompt 使用。"""
        return "\n".join(f"[{u.speaker}] {u.text}" for u in self.utterances)

    @property
    def duration_sec(self) -> float:
        return (self.utterances[-1].end_ms - self.utterances[0].begin_ms) / 1000 if self.utterances else 0


def transcribe(audio_url: str) -> Transcript:
    """转写一段可公网访问的录音，返回带说话人标签的 Transcript。"""
    import dashscope
    from dashscope.audio.asr import Transcription

    dashscope.api_key = ensure_api_key()

    task_resp = Transcription.async_call(
        model=ASR_MODEL,
        file_urls=[audio_url],
        diarization_enabled=True,
        speaker_count=2,
    )
    result = Transcription.wait(task=task_resp.output.task_id)

    if result.status_code != 200:
        raise RuntimeError(f"ASR 任务失败: {result.status_code} {result.message}")

    try:
        transcript_info = result.output["results"][0]["transcription"]["transcripts"][0]
        sentences = transcript_info.get("sentences", [])
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"ASR 返回结构不符合预期: {result.output}") from e

    # diarization 输出的 speaker_id 只有 0/1，谁是谁需要用户在界面上确认/翻转
    utt_list = []
    for s in sentences:
        speaker = "interviewer" if s.get("speaker_id", 0) == 0 else "candidate"
        utt_list.append(
            Utterance(
                speaker=speaker,
                text=s.get("text", "").strip(),
                begin_ms=s.get("begin_time", 0),
                end_ms=s.get("end_time", 0),
            )
        )

    if not utt_list:
        raise ValueError("转写结果为空，请检查录音是否有效、语言是否为中文。")
    return Transcript(utterances=utt_list)

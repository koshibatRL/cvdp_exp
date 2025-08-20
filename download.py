#!/usr/bin/env python3

import os
from datasets import load_dataset

def download_cvdp_dataset():
    """CVDPデータセットをダウンロード"""
    
    # HF_HOME環境変数をチェック
    hf_home = os.environ.get('HF_HOME')
    if not hf_home:
        print("❌ HF_HOME環境変数が設定されていません")
        return None
    
    print(f"🤗 CVDPデータセットをダウンロード中...")
    print(f"キャッシュ先: {hf_home}")
    
    try:
        # データセットをダウンロード
        dataset = load_dataset("nvidia/cvdp-benchmark-dataset", "cvdp_nonagentic_code_generation_no_commercial")
        
        print("✅ ダウンロード完了!")
        return dataset
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print("認証が必要な場合は 'huggingface-cli login' を実行してください")
        return None

if __name__ == "__main__":
    download_cvdp_dataset()
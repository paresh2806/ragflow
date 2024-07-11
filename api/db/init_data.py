#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import json
import os
import time
import uuid
from copy import deepcopy

from api.db import LLMType, UserTenantRole
from api.db.db_models import init_database_tables as init_web_db, LLMFactories, LLM, TenantLLM
from api.db.services import UserService
from api.db.services.canvas_service import CanvasTemplateService
from api.db.services.document_service import DocumentService
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.llm_service import LLMFactoriesService, LLMService, TenantLLMService, LLMBundle
from api.db.services.user_service import TenantService, UserTenantService
from api.settings import CHAT_MDL, EMBEDDING_MDL, ASR_MDL, IMAGE2TEXT_MDL, PARSERS, LLM_FACTORY, API_KEY, LLM_BASE_URL
from api.utils.file_utils import get_project_base_directory


def init_superuser():
    user_info = {
        "id": uuid.uuid1().hex,
        "password": "admin",
        "nickname": "admin",
        "is_superuser": True,
        "email": "admin@ragflow.io",
        "creator": "system",
        "status": "1",
    }
    tenant = {
        "id": user_info["id"],
        "name": user_info["nickname"] + "‘s Kingdom",
        "llm_id": CHAT_MDL,
        "embd_id": EMBEDDING_MDL,
        "asr_id": ASR_MDL,
        "parser_ids": PARSERS,
        "img2txt_id": IMAGE2TEXT_MDL
    }
    usr_tenant = {
        "tenant_id": user_info["id"],
        "user_id": user_info["id"],
        "invited_by": user_info["id"],
        "role": UserTenantRole.OWNER
    }
    tenant_llm = []
    for llm in LLMService.query(fid=LLM_FACTORY):
        tenant_llm.append(
            {"tenant_id": user_info["id"], "llm_factory": LLM_FACTORY, "llm_name": llm.llm_name, "model_type": llm.model_type,
             "api_key": API_KEY, "api_base": LLM_BASE_URL})

    if not UserService.save(**user_info):
        print("\033[93m【ERROR】\033[0mcan't init admin.")
        return
    TenantService.insert(**tenant)
    UserTenantService.insert(**usr_tenant)
    TenantLLMService.insert_many(tenant_llm)
    print(
        "【INFO】Super user initialized. \033[93memail: admin@ragflow.io, password: admin\033[0m. Changing the password after logining is strongly recomanded.")

    chat_mdl = LLMBundle(tenant["id"], LLMType.CHAT, tenant["llm_id"])
    msg = chat_mdl.chat(system="", history=[
                        {"role": "user", "content": "Hello!"}], gen_conf={})
    if msg.find("ERROR: ") == 0:
        print(
            "\33[91m【ERROR】\33[0m: ",
            "'{}' dosen't work. {}".format(
                tenant["llm_id"],
                msg))
    embd_mdl = LLMBundle(tenant["id"], LLMType.EMBEDDING, tenant["embd_id"])
    v, c = embd_mdl.encode(["Hello!"])
    if c == 0:
        print(
            "\33[91m【ERROR】\33[0m:",
            " '{}' dosen't work!".format(
                tenant["embd_id"]))


factory_infos = [{
    "name": "OpenAI",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING,SPEECH2TEXT,MODERATION",
    "status": "1",
}, {
    "name": "Tongyi-Qianwen",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING,SPEECH2TEXT,MODERATION",
    "status": "1",
}, {
    "name": "ZHIPU-AI",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING,SPEECH2TEXT,MODERATION",
    "status": "1",
},
    {
    "name": "Ollama",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING,SPEECH2TEXT,MODERATION",
        "status": "1",
}, {
    "name": "Moonshot",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING",
    "status": "1",
}, {
    "name": "FastEmbed",
    "logo": "",
    "tags": "TEXT EMBEDDING",
    "status": "1",
}, {
    "name": "Xinference",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING,SPEECH2TEXT,MODERATION",
        "status": "1",
},{
    "name": "Youdao",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING,SPEECH2TEXT,MODERATION",
    "status": "1",
},{
    "name": "DeepSeek",
    "logo": "",
    "tags": "LLM",
    "status": "1",
},{
    "name": "VolcEngine",
    "logo": "",
    "tags": "LLM, TEXT EMBEDDING",
    "status": "1",
},{
    "name": "BaiChuan",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING",
    "status": "1",
},{
    "name": "Jina",
    "logo": "",
    "tags": "TEXT EMBEDDING, TEXT RE-RANK",
    "status": "1",
},{
    "name": "BAAI",
    "logo": "",
    "tags": "TEXT EMBEDDING, TEXT RE-RANK",
    "status": "1",
},{
    "name": "MiniMax",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING",
    "status": "1",
},{
    "name": "Mistral",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING",
    "status": "1",
},{
    "name": "Azure-OpenAI",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING,SPEECH2TEXT,MODERATION",
    "status": "1",
},{
    "name": "Bedrock",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING",
    "status": "1",
},{
    "name": "Gemini",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING,IMAGE2TEXT",
    "status": "1",
},
{
    "name": "Groq",
    "logo": "",
    "tags": "LLM",
    "status": "1",
}
    # {
    #     "name": "文心一言",
    #     "logo": "",
    #     "tags": "LLM,TEXT EMBEDDING,SPEECH2TEXT,MODERATION",
    #     "status": "1",
    # },
]


def init_llm_factory():
    llm_infos = [
        # ---------------------- OpenAI ------------------------
        {
            "fid": factory_infos[0]["name"],
            "llm_name": "gpt-4o",
            "tags": "LLM,CHAT,128K",
            "max_tokens": 128000,
            "model_type": LLMType.CHAT.value + "," + LLMType.IMAGE2TEXT.value
        }, {
            "fid": factory_infos[0]["name"],
            "llm_name": "gpt-3.5-turbo",
            "tags": "LLM,CHAT,4K",
            "max_tokens": 4096,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[0]["name"],
            "llm_name": "gpt-3.5-turbo-16k-0613",
            "tags": "LLM,CHAT,16k",
            "max_tokens": 16385,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[0]["name"],
            "llm_name": "text-embedding-ada-002",
            "tags": "TEXT EMBEDDING,8K",
            "max_tokens": 8191,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[0]["name"],
            "llm_name": "text-embedding-3-small",
            "tags": "TEXT EMBEDDING,8K",
            "max_tokens": 8191,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[0]["name"],
            "llm_name": "text-embedding-3-large",
            "tags": "TEXT EMBEDDING,8K",
            "max_tokens": 8191,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[0]["name"],
            "llm_name": "whisper-1",
            "tags": "SPEECH2TEXT",
            "max_tokens": 25 * 1024 * 1024,
            "model_type": LLMType.SPEECH2TEXT.value
        }, {
            "fid": factory_infos[0]["name"],
            "llm_name": "gpt-4",
            "tags": "LLM,CHAT,8K",
            "max_tokens": 8191,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[0]["name"],
            "llm_name": "gpt-4-turbo",
            "tags": "LLM,CHAT,8K",
            "max_tokens": 8191,
            "model_type": LLMType.CHAT.value
        },{
            "fid": factory_infos[0]["name"],
            "llm_name": "gpt-4-32k",
            "tags": "LLM,CHAT,32K",
            "max_tokens": 32768,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[0]["name"],
            "llm_name": "gpt-4-vision-preview",
            "tags": "LLM,CHAT,IMAGE2TEXT",
            "max_tokens": 765,
            "model_type": LLMType.IMAGE2TEXT.value
        },
        # ----------------------- Qwen -----------------------
        {
            "fid": factory_infos[1]["name"],
            "llm_name": "qwen-turbo",
            "tags": "LLM,CHAT,8K",
            "max_tokens": 8191,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[1]["name"],
            "llm_name": "qwen-plus",
            "tags": "LLM,CHAT,32K",
            "max_tokens": 32768,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[1]["name"],
            "llm_name": "qwen-max-1201",
            "tags": "LLM,CHAT,6K",
            "max_tokens": 5899,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[1]["name"],
            "llm_name": "text-embedding-v2",
            "tags": "TEXT EMBEDDING,2K",
            "max_tokens": 2048,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[1]["name"],
            "llm_name": "paraformer-realtime-8k-v1",
            "tags": "SPEECH2TEXT",
            "max_tokens": 25 * 1024 * 1024,
            "model_type": LLMType.SPEECH2TEXT.value
        }, {
            "fid": factory_infos[1]["name"],
            "llm_name": "qwen-vl-max",
            "tags": "LLM,CHAT,IMAGE2TEXT",
            "max_tokens": 765,
            "model_type": LLMType.IMAGE2TEXT.value
        },
        # ---------------------- ZhipuAI ----------------------
        {
            "fid": factory_infos[2]["name"],
            "llm_name": "glm-3-turbo",
            "tags": "LLM,CHAT,",
            "max_tokens": 128 * 1000,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[2]["name"],
            "llm_name": "glm-4",
            "tags": "LLM,CHAT,",
            "max_tokens": 128 * 1000,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[2]["name"],
            "llm_name": "glm-4v",
            "tags": "LLM,CHAT,IMAGE2TEXT",
            "max_tokens": 2000,
            "model_type": LLMType.IMAGE2TEXT.value
        },
        {
            "fid": factory_infos[2]["name"],
            "llm_name": "embedding-2",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 512,
            "model_type": LLMType.EMBEDDING.value
        },
        # ------------------------ Moonshot -----------------------
        {
            "fid": factory_infos[4]["name"],
            "llm_name": "moonshot-v1-8k",
            "tags": "LLM,CHAT,",
            "max_tokens": 7900,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[4]["name"],
            "llm_name": "moonshot-v1-32k",
            "tags": "LLM,CHAT,",
            "max_tokens": 32768,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[4]["name"],
            "llm_name": "moonshot-v1-128k",
            "tags": "LLM,CHAT",
            "max_tokens": 128 * 1000,
            "model_type": LLMType.CHAT.value
        },
        # ------------------------ FastEmbed -----------------------
        {
            "fid": factory_infos[5]["name"],
            "llm_name": "BAAI/bge-small-en-v1.5",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 512,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[5]["name"],
            "llm_name": "BAAI/bge-small-zh-v1.5",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 512,
            "model_type": LLMType.EMBEDDING.value
        }, {
        }, {
            "fid": factory_infos[5]["name"],
            "llm_name": "BAAI/bge-base-en-v1.5",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 512,
            "model_type": LLMType.EMBEDDING.value
        }, {
        }, {
            "fid": factory_infos[5]["name"],
            "llm_name": "BAAI/bge-large-en-v1.5",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 512,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[5]["name"],
            "llm_name": "sentence-transformers/all-MiniLM-L6-v2",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 512,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[5]["name"],
            "llm_name": "nomic-ai/nomic-embed-text-v1.5",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 8192,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[5]["name"],
            "llm_name": "jinaai/jina-embeddings-v2-small-en",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 2147483648,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[5]["name"],
            "llm_name": "jinaai/jina-embeddings-v2-base-en",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 2147483648,
            "model_type": LLMType.EMBEDDING.value
        },
        # ------------------------ Youdao -----------------------
        {
            "fid": factory_infos[7]["name"],
            "llm_name": "maidalun1020/bce-embedding-base_v1",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 512,
            "model_type": LLMType.EMBEDDING.value
        },
        {
            "fid": factory_infos[7]["name"],
            "llm_name": "maidalun1020/bce-reranker-base_v1",
            "tags": "RE-RANK, 512",
            "max_tokens": 512,
            "model_type": LLMType.RERANK.value
        },
        # ------------------------ DeepSeek -----------------------
        {
            "fid": factory_infos[8]["name"],
            "llm_name": "deepseek-chat",
            "tags": "LLM,CHAT,",
            "max_tokens": 32768,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[8]["name"],
            "llm_name": "deepseek-coder",
            "tags": "LLM,CHAT,",
            "max_tokens": 16385,
            "model_type": LLMType.CHAT.value
        },
        # ------------------------ VolcEngine -----------------------
        {
            "fid": factory_infos[9]["name"],
            "llm_name": "Skylark2-pro-32k",
            "tags": "LLM,CHAT,32k",
            "max_tokens": 32768,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[9]["name"],
            "llm_name": "Skylark2-pro-4k",
            "tags": "LLM,CHAT,4k",
            "max_tokens": 4096,
            "model_type": LLMType.CHAT.value
        },
        # ------------------------ BaiChuan -----------------------
        {
            "fid": factory_infos[10]["name"],
            "llm_name": "Baichuan2-Turbo",
            "tags": "LLM,CHAT,32K",
            "max_tokens": 32768,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[10]["name"],
            "llm_name": "Baichuan2-Turbo-192k",
            "tags": "LLM,CHAT,192K",
            "max_tokens": 196608,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[10]["name"],
            "llm_name": "Baichuan3-Turbo",
            "tags": "LLM,CHAT,32K",
            "max_tokens": 32768,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[10]["name"],
            "llm_name": "Baichuan3-Turbo-128k",
            "tags": "LLM,CHAT,128K",
            "max_tokens": 131072,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[10]["name"],
            "llm_name": "Baichuan4",
            "tags": "LLM,CHAT,128K",
            "max_tokens": 131072,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[10]["name"],
            "llm_name": "Baichuan-Text-Embedding",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 512,
            "model_type": LLMType.EMBEDDING.value
        },
        # ------------------------ Jina -----------------------
        {
            "fid": factory_infos[11]["name"],
            "llm_name": "jina-reranker-v1-base-en",
            "tags": "RE-RANK,8k",
            "max_tokens": 8196,
            "model_type": LLMType.RERANK.value
        },
        {
            "fid": factory_infos[11]["name"],
            "llm_name": "jina-reranker-v1-turbo-en",
            "tags": "RE-RANK,8k",
            "max_tokens": 8196,
            "model_type": LLMType.RERANK.value
        },
        {
            "fid": factory_infos[11]["name"],
            "llm_name": "jina-reranker-v1-tiny-en",
            "tags": "RE-RANK,8k",
            "max_tokens": 8196,
            "model_type": LLMType.RERANK.value
        },
        {
            "fid": factory_infos[11]["name"],
            "llm_name": "jina-colbert-v1-en",
            "tags": "RE-RANK,8k",
            "max_tokens": 8196,
            "model_type": LLMType.RERANK.value
        },
        {
            "fid": factory_infos[11]["name"],
            "llm_name": "jina-embeddings-v2-base-en",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 8196,
            "model_type": LLMType.EMBEDDING.value
        },
        {
            "fid": factory_infos[11]["name"],
            "llm_name": "jina-embeddings-v2-base-de",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 8196,
            "model_type": LLMType.EMBEDDING.value
        },
        {
            "fid": factory_infos[11]["name"],
            "llm_name": "jina-embeddings-v2-base-es",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 8196,
            "model_type": LLMType.EMBEDDING.value
        },
        {
            "fid": factory_infos[11]["name"],
            "llm_name": "jina-embeddings-v2-base-code",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 8196,
            "model_type": LLMType.EMBEDDING.value
        },
        {
            "fid": factory_infos[11]["name"],
            "llm_name": "jina-embeddings-v2-base-zh",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 8196,
            "model_type": LLMType.EMBEDDING.value
        },
        # ------------------------ BAAI -----------------------
        {
            "fid": factory_infos[12]["name"],
            "llm_name": "BAAI/bge-large-zh-v1.5",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 1024,
            "model_type": LLMType.EMBEDDING.value
        },
        {
            "fid": factory_infos[12]["name"],
            "llm_name": "BAAI/bge-reranker-v2-m3",
            "tags": "RE-RANK,2k",
            "max_tokens": 2048,
            "model_type": LLMType.RERANK.value
        },
        # ------------------------ Minimax -----------------------
        {
            "fid": factory_infos[13]["name"],
            "llm_name": "abab6.5-chat",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[13]["name"],
            "llm_name": "abab6.5s-chat",
            "tags": "LLM,CHAT,245k",
            "max_tokens": 245760,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[13]["name"],
            "llm_name": "abab6.5t-chat",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[13]["name"],
            "llm_name": "abab6.5g-chat",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[13]["name"],
            "llm_name": "abab5.5-chat",
            "tags": "LLM,CHAT,16k",
            "max_tokens": 16384,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[13]["name"],
            "llm_name": "abab5.5s-chat",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.CHAT.value
        },
        # ------------------------ Mistral -----------------------
        {
            "fid": factory_infos[14]["name"],
            "llm_name": "open-mixtral-8x22b",
            "tags": "LLM,CHAT,64k",
            "max_tokens": 64000,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[14]["name"],
            "llm_name": "open-mixtral-8x7b",
            "tags": "LLM,CHAT,32k",
            "max_tokens": 32000,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[14]["name"],
            "llm_name": "open-mistral-7b",
            "tags": "LLM,CHAT,32k",
            "max_tokens": 32000,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[14]["name"],
            "llm_name": "mistral-large-latest",
            "tags": "LLM,CHAT,32k",
            "max_tokens": 32000,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[14]["name"],
            "llm_name": "mistral-small-latest",
            "tags": "LLM,CHAT,32k",
            "max_tokens": 32000,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[14]["name"],
            "llm_name": "mistral-medium-latest",
            "tags": "LLM,CHAT,32k",
            "max_tokens": 32000,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[14]["name"],
            "llm_name": "codestral-latest",
            "tags": "LLM,CHAT,32k",
            "max_tokens": 32000,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[14]["name"],
            "llm_name": "mistral-embed",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.EMBEDDING
        },
        # ------------------------ Azure OpenAI -----------------------
        #  Please ensure the llm_name is the same as the name in Azure
        #  OpenAI deployment name (e.g., azure-gpt-4o). And the llm_name
        #  must different from the OpenAI llm_name
        #
        #  Each model must be deployed in the Azure OpenAI service, otherwise,
        #  you will receive an error message 'The API deployment for
        #  this resource does not exist'
        {
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-gpt-4o",
            "tags": "LLM,CHAT,128K",
            "max_tokens": 128000,
            "model_type": LLMType.CHAT.value + "," + LLMType.IMAGE2TEXT.value
        }, {
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-gpt-35-turbo",
            "tags": "LLM,CHAT,4K",
            "max_tokens": 4096,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-gpt-35-turbo-16k",
            "tags": "LLM,CHAT,16k",
            "max_tokens": 16385,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-text-embedding-ada-002",
            "tags": "TEXT EMBEDDING,8K",
            "max_tokens": 8191,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-text-embedding-3-small",
            "tags": "TEXT EMBEDDING,8K",
            "max_tokens": 8191,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-text-embedding-3-large",
            "tags": "TEXT EMBEDDING,8K",
            "max_tokens": 8191,
            "model_type": LLMType.EMBEDDING.value
        },{
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-whisper-1",
            "tags": "SPEECH2TEXT",
            "max_tokens": 25 * 1024 * 1024,
            "model_type": LLMType.SPEECH2TEXT.value
         },
        {
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-gpt-4",
            "tags": "LLM,CHAT,8K",
            "max_tokens": 8191,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-gpt-4-turbo",
            "tags": "LLM,CHAT,8K",
            "max_tokens": 8191,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-gpt-4-32k",
            "tags": "LLM,CHAT,32K",
            "max_tokens": 32768,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[15]["name"],
            "llm_name": "azure-gpt-4-vision-preview",
            "tags": "LLM,CHAT,IMAGE2TEXT",
            "max_tokens": 765,
            "model_type": LLMType.IMAGE2TEXT.value
        },
        # ------------------------ Bedrock -----------------------
        {
            "fid": factory_infos[16]["name"],
            "llm_name": "ai21.j2-ultra-v1",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8191,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "ai21.j2-mid-v1",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8191,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "cohere.command-text-v14",
            "tags": "LLM,CHAT,4k",
            "max_tokens": 4096,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "cohere.command-light-text-v14",
            "tags": "LLM,CHAT,4k",
            "max_tokens": 4096,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "cohere.command-r-v1:0",
            "tags": "LLM,CHAT,128k",
            "max_tokens": 128 * 1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "cohere.command-r-plus-v1:0",
            "tags": "LLM,CHAT,128k",
            "max_tokens": 128000,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "anthropic.claude-v2",
            "tags": "LLM,CHAT,100k",
            "max_tokens": 100 * 1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "anthropic.claude-v2:1",
            "tags": "LLM,CHAT,200k",
            "max_tokens": 200 * 1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "anthropic.claude-3-sonnet-20240229-v1:0",
            "tags": "LLM,CHAT,200k",
            "max_tokens": 200 * 1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "tags": "LLM,CHAT,200k",
            "max_tokens": 200 * 1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "anthropic.claude-3-haiku-20240307-v1:0",
            "tags": "LLM,CHAT,200k",
            "max_tokens": 200 * 1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "anthropic.claude-3-opus-20240229-v1:0",
            "tags": "LLM,CHAT,200k",
            "max_tokens": 200 * 1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "anthropic.claude-instant-v1",
            "tags": "LLM,CHAT,100k",
            "max_tokens": 100 * 1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "amazon.titan-text-express-v1",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "amazon.titan-text-premier-v1:0",
            "tags": "LLM,CHAT,32k",
            "max_tokens": 32 * 1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "amazon.titan-text-lite-v1",
            "tags": "LLM,CHAT,4k",
            "max_tokens": 4096,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "meta.llama2-13b-chat-v1",
            "tags": "LLM,CHAT,4k",
            "max_tokens": 4096,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "meta.llama2-70b-chat-v1",
            "tags": "LLM,CHAT,4k",
            "max_tokens": 4096,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "meta.llama3-8b-instruct-v1:0",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "meta.llama3-70b-instruct-v1:0",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "mistral.mistral-7b-instruct-v0:2",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "mistral.mixtral-8x7b-instruct-v0:1",
            "tags": "LLM,CHAT,4k",
            "max_tokens": 4096,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "mistral.mistral-large-2402-v1:0",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "mistral.mistral-small-2402-v1:0",
            "tags": "LLM,CHAT,8k",
            "max_tokens": 8192,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "amazon.titan-embed-text-v2:0",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 8192,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "cohere.embed-english-v3",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 2048,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[16]["name"],
            "llm_name": "cohere.embed-multilingual-v3",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 2048,
            "model_type": LLMType.EMBEDDING.value
        }, {
            "fid": factory_infos[17]["name"],
            "llm_name": "gemini-1.5-pro-latest",
            "tags": "LLM,CHAT,1024K",
            "max_tokens": 1024*1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[17]["name"],
            "llm_name": "gemini-1.5-flash-latest",
            "tags": "LLM,CHAT,1024K",
            "max_tokens": 1024*1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[17]["name"],
            "llm_name": "gemini-1.0-pro",
            "tags": "LLM,CHAT,30K",
            "max_tokens": 30*1024,
            "model_type": LLMType.CHAT.value
        }, {
            "fid": factory_infos[17]["name"],
            "llm_name": "gemini-1.0-pro-vision-latest",
            "tags": "LLM,IMAGE2TEXT,12K",
            "max_tokens": 12*1024,
            "model_type": LLMType.IMAGE2TEXT.value
        }, {
            "fid": factory_infos[17]["name"],
            "llm_name": "text-embedding-004",
            "tags": "TEXT EMBEDDING",
            "max_tokens": 2048,
            "model_type": LLMType.EMBEDDING.value
        },
        # ------------------------ Groq -----------------------
        {
            "fid": factory_infos[18]["name"],
            "llm_name": "gemma-7b-it",
            "tags": "LLM,CHAT,15k",
            "max_tokens": 8192,

            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[18]["name"],
            "llm_name": "gemma2-9b-it",
            "tags": "LLM,CHAT,15k",
            "max_tokens": 8192,

            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[18]["name"],
            "llm_name": "llama3-70b-8192",
            "tags": "LLM,CHAT,6k",
            "max_tokens": 8192,

            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[18]["name"],
            "llm_name": "llama3-8b-8192",
            "tags": "LLM,CHAT,30k",
            "max_tokens": 8192,

            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[18]["name"],
            "llm_name": "mixtral-8x7b-32768",
            "tags": "LLM,CHAT,5k",
            "max_tokens": 32768,

            "model_type": LLMType.CHAT.value
        }
    ]
    for info in factory_infos:
        try:
            LLMFactoriesService.save(**info)
        except Exception as e:
            pass
    for info in llm_infos:
        try:
            LLMService.save(**info)
        except Exception as e:
            pass

    LLMFactoriesService.filter_delete([LLMFactories.name == "Local"])
    LLMService.filter_delete([LLM.fid == "Local"])
    LLMService.filter_delete([LLM.fid == "Moonshot", LLM.llm_name == "flag-embedding"])
    TenantLLMService.filter_delete([TenantLLM.llm_factory == "Moonshot", TenantLLM.llm_name == "flag-embedding"])
    LLMFactoriesService.filter_delete([LLMFactoriesService.model.name == "QAnything"])
    LLMService.filter_delete([LLMService.model.fid == "QAnything"])
    TenantLLMService.filter_update([TenantLLMService.model.llm_factory == "QAnything"], {"llm_factory": "Youdao"})
    ## insert openai two embedding models to the current openai user.
    print("Start to insert 2 OpenAI embedding models...")
    tenant_ids = set([row["tenant_id"] for row in TenantLLMService.get_openai_models()])
    for tid in tenant_ids:
        for row in TenantLLMService.query(llm_factory="OpenAI", tenant_id=tid):
            row = row.to_dict()
            row["model_type"] = LLMType.EMBEDDING.value
            row["llm_name"] = "text-embedding-3-small"
            row["used_tokens"] = 0
            try:
                TenantLLMService.save(**row)
                row = deepcopy(row)
                row["llm_name"] = "text-embedding-3-large"
                TenantLLMService.save(**row)
            except Exception as e:
                pass
            break
    for kb_id in KnowledgebaseService.get_all_ids():
        KnowledgebaseService.update_by_id(kb_id, {"doc_num": DocumentService.get_kb_doc_count(kb_id)})
    """
    drop table llm;
    drop table llm_factories;
    update tenant set parser_ids='naive:General,qa:Q&A,resume:Resume,manual:Manual,table:Table,paper:Paper,book:Book,laws:Laws,presentation:Presentation,picture:Picture,one:One';
    alter table knowledgebase modify avatar longtext;
    alter table user modify avatar longtext;
    alter table dialog modify icon longtext;
    """


def add_graph_templates():
    dir = os.path.join(get_project_base_directory(), "graph", "templates")
    for fnm in os.listdir(dir):
        try:
            cnvs = json.load(open(os.path.join(dir, fnm), "r"))
            try:
                CanvasTemplateService.save(**cnvs)
            except:
                CanvasTemplateService.update_by_id(cnvs["id"], cnvs)
        except Exception as e:
            print("Add graph templates error: ", e)
            print("------------", flush=True)


def init_web_data():
    start_time = time.time()

    init_llm_factory()
    if not UserService.get_all().count():
        init_superuser()

    add_graph_templates()
    print("init web data success:{}".format(time.time() - start_time))


if __name__ == '__main__':
    init_web_db()
    init_web_data()

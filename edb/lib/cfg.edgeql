#
# This source file is part of the EdgeDB open source project.
#
# Copyright 2018-present MagicStack Inc. and the EdgeDB authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


CREATE MODULE cfg;


CREATE ABSTRACT ATTRIBUTE cfg::backend_setting;
CREATE ABSTRACT ATTRIBUTE cfg::internal;
CREATE ABSTRACT ATTRIBUTE cfg::requires_restart;
CREATE ABSTRACT ATTRIBUTE cfg::system;


CREATE TYPE cfg::Port {
    CREATE REQUIRED PROPERTY port -> std::int64 {
        CREATE CONSTRAINT std::exclusive;
        SET readonly := true;
    };

    CREATE REQUIRED PROPERTY protocol -> std::str {
        SET readonly := true;
    };

    CREATE REQUIRED PROPERTY database -> std::str {
        SET readonly := true;
    };

    CREATE REQUIRED PROPERTY concurrency -> std::int64 {
        SET readonly := true;
    };

    CREATE REQUIRED PROPERTY user -> std::str {
        SET readonly := true;
    };

    CREATE REQUIRED MULTI PROPERTY address -> std::str {
        SET readonly := true;
        SET default := {'localhost'};
    };
};


CREATE ABSTRACT TYPE cfg::AuthMethod;
CREATE TYPE cfg::Trust EXTENDING cfg::AuthMethod;
CREATE TYPE cfg::SCRAM EXTENDING cfg::AuthMethod;


CREATE TYPE cfg::Auth {
    CREATE REQUIRED PROPERTY name -> std::str {
        CREATE CONSTRAINT std::exclusive;
        SET readonly := true;
    };

    CREATE REQUIRED PROPERTY priority -> std::int64 {
        CREATE CONSTRAINT std::exclusive;
        SET readonly := true;
    };

    CREATE REQUIRED MULTI PROPERTY host -> std::str {
        SET readonly := true;
        SET default := {'*'};
    };

    CREATE MULTI PROPERTY user -> std::str {
        SET readonly := true;
        SET default := {'*'};
    };

    CREATE MULTI PROPERTY database -> std::str {
        SET readonly := true;
        SET default := {'*'};
    };

    CREATE SINGLE LINK method -> cfg::AuthMethod {
        CREATE CONSTRAINT std::exclusive;
    };
};


CREATE TYPE cfg::Config {
    CREATE MULTI LINK ports -> cfg::Port {
        SET ATTRIBUTE cfg::system := 'true';
    };

    CREATE MULTI LINK auth -> cfg::Auth {
        SET ATTRIBUTE cfg::system := 'true';
    };

    # Exposed backend settings follow.

    CREATE PROPERTY shared_buffers -> std::str {
        SET ATTRIBUTE cfg::system := 'true';
        SET ATTRIBUTE cfg::backend_setting := '"shared_buffers"';
        SET ATTRIBUTE cfg::requires_restart := 'true';
        SET default := '-1';
    };

    CREATE PROPERTY query_work_mem -> std::str {
        SET ATTRIBUTE cfg::backend_setting := '"work_mem"';
        SET default := '-1';
    };

    CREATE PROPERTY effective_cache_size -> std::str {
        SET ATTRIBUTE cfg::backend_setting := '"effective_cache_size"';
        SET default := '-1';
    };

    CREATE PROPERTY effective_io_concurrency -> std::str {
        SET ATTRIBUTE cfg::backend_setting := '"effective_io_concurrency"';
        SET default := '50';
    };

    CREATE PROPERTY default_statistics_target -> std::str {
        SET ATTRIBUTE cfg::backend_setting := '"default_statistics_target"';
        SET default := '100';
    };
};


CREATE FUNCTION
cfg::get_config_json() -> std::json
{
    FROM SQL $$
    SELECT jsonb_object_agg(cfg.name, cfg)
    FROM edgedb._read_sys_config() AS cfg
    $$;
};
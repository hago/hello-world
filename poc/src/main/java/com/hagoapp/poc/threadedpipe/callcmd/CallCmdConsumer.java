/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe.callcmd;

import com.hagoapp.poc.threadedpipe.Consumer;
import com.hagoapp.poc.threadedpipe.ConsumerConfig;

import java.nio.charset.StandardCharsets;

public class CallCmdConsumer extends Consumer {

    private CallCmdConsumerConfig config;

    @Override
    public void loadConfig(ConsumerConfig config) {
        if (!(config instanceof CallCmdConsumerConfig)) {
            throw new UnsupportedOperationException("not a call cmd config");
        }
        this.config = (CallCmdConsumerConfig) config;
    }

    @Override
    public String supportConsumerType() {
        return CallCmdConsumerConfig.CALL_CMD;
    }

    @Override
    public String getName() {
        return String.format("Cmd Caller: %s %s", config.getCmd(), String.join(" ", config.getArguments()));
    }

    @Override
    public void run() {
        try {
            var p = Runtime.getRuntime().exec(config.getCmd(), config.getArguments().toArray(new String[0]));
            var s = new String(p.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
            var err = new String(p.getErrorStream().readAllBytes(), StandardCharsets.UTF_8);
            logger.info("{} output: {}", getName(), s);
            logger.error("{} errout: {}", getName(), err);
        } catch (Exception e) {
            logger.error("Error {} for {}", e.getMessage(), getName());
        }
    }
}

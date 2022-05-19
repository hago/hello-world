/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe.callcmd;

import com.hagoapp.poc.threadedpipe.ConsumerConfig;

import java.util.ArrayList;
import java.util.List;

public class CallCmdConsumerConfig implements ConsumerConfig {

    public static final String CALL_CMD = "com.hagoapp.poc.threadedpipe.callcmd";

    @Override
    public String getConsumerType() {
        return CALL_CMD;
    }

    private String cmd;
    private List<String> arguments = new ArrayList<>();

    public String getCmd() {
        return cmd;
    }

    public void setCmd(String cmd) {
        this.cmd = cmd;
    }

    public List<String> getArguments() {
        return arguments;
    }

    public void setArguments(List<String> arguments) {
        this.arguments = arguments;
    }
}

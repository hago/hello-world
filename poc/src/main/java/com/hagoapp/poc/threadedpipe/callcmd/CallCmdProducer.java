/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe.callcmd;

import com.hagoapp.poc.threadedpipe.ConsumerConfig;
import com.hagoapp.poc.threadedpipe.Producer;

public class CallCmdProducer implements Producer {

    @Override
    public ConsumerConfig createConsumerConfig() {
        var cfg = new CallCmdConsumerConfig();
        cfg.setCmd("date");
        return cfg;
    }
}

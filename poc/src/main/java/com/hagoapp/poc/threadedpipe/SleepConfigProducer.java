/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe;

import java.util.UUID;

public class SleepConfigProducer implements Producer {

    private final String id = UUID.randomUUID().toString();

    @Override
    public synchronized SleepConsumerConfig createConsumerConfig() {
        var t = new SleepConsumerConfig();
        t.setName("Sleep Consumer: " + id);
        return t;
    }
}

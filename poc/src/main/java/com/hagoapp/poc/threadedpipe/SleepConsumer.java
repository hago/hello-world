/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe;

import java.time.Instant;
import java.util.Random;
import java.util.concurrent.TimeUnit;

public class SleepConsumer extends Consumer {

    private SleepConsumerConfig config;

    @Override
    public void run() {
        var duration = new Random(Instant.now().toEpochMilli()).nextInt(500);
        try {
            TimeUnit.MILLISECONDS.sleep(duration);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        logger.info("running {} for {}", config.getName(), duration);
    }

    @Override
    public String getName() {
        return config.getName();
    }

    @Override
    public void loadConfig(ConsumerConfig config) {
        if (!(config instanceof SleepConsumerConfig)) {
            throw new UnsupportedOperationException("not a sleep config");
        }
        this.config = (SleepConsumerConfig) config;
    }

    @Override
    public String supportConsumerType() {
        return SleepConsumerConfig.SLEEP_CONSUMER;
    }
}

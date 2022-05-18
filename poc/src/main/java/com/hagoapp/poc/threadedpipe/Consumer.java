/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe;

import com.hagoapp.poc.AppLogger;
import org.slf4j.Logger;

import java.time.Instant;
import java.util.Random;
import java.util.concurrent.TimeUnit;

public class Consumer implements Runnable {

    private final TaskConfig config;
    private final Logger logger = AppLogger.getLogger();

    public Consumer(TaskConfig cfg) {
        config = cfg;
    }

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

    public String getName() {
        return config.getName();
    }
}

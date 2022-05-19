/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe;

import com.hagoapp.poc.AppLogger;
import org.slf4j.Logger;

import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class ThreadedPipe {

    private static final LinkedBlockingQueue<Runnable> threadQueue = new LinkedBlockingQueue<>();
    private static ThreadPoolExecutor pool;
    private static final Logger logger = AppLogger.getLogger();

    public static void run(int minThreadCount, int maxThreadCount, int count) {
        pool = new ThreadPoolExecutor(minThreadCount, maxThreadCount, 0,
                TimeUnit.SECONDS,
                threadQueue);
        var generated = 0;
        logger.info("enter loop");
        var producer = new SleepConfigProducer();
        while (generated < count) {
            if (threadQueue.size() >= pool.getMaximumPoolSize()) {
                logger.info("pool full, sleep");
                try {
                    Thread.sleep(1000);
                    continue;
                } catch (InterruptedException e) {
                    continue;
                }
            }
            //logger.info("queue {} maximum {}", threadQueue.size(), pool.getMaximumPoolSize());
            var newConfig = producer.createConsumerConfig();
            if (newConfig == null) {
                break;
            }
            var consumer = ConsumerFactory.createConsumer(newConfig);
            pool.execute(consumer);
            generated++;
            logger.info("consumer added: {}, no. {}", consumer.getName(), generated);
        }
        while (pool.getActiveCount() > 0) {
            try {
                logger.info("Active tasks: {}", pool.getActiveCount());
                Thread.sleep(500);
            } catch (InterruptedException e) {
                //
            }
        }
        logger.info("shutdown pool");
        pool.shutdown();
    }
}

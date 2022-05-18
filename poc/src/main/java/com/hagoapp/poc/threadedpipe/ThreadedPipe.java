/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe;

import com.hagoapp.poc.AppLogger;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class ThreadedPipe {

    private static final LinkedBlockingQueue<Runnable> threadQueue = new LinkedBlockingQueue<>();
    private static ThreadPoolExecutor pool;
    private static final Logger logger = AppLogger.getLogger();

    public static void run(int minThreadCount, int maxThreadCount) {
        pool = new ThreadPoolExecutor(minThreadCount, maxThreadCount, 0,
                TimeUnit.SECONDS,
                threadQueue);
        var generator = TaskConfigGenerator.CreateGenerator(1000);
        logger.info("enter loop");
        while (true) {
            if (threadQueue.size() >= pool.getMaximumPoolSize()) {
                logger.info("pool full, sleep");
                try {
                    Thread.sleep(1000);
                    continue;
                } catch (InterruptedException e) {
                    continue;
                }
            }
            logger.info("queue {} maximum {}", threadQueue.size(), pool.getMaximumPoolSize());
            var newTaskConfig = generator.getTask();
            if (newTaskConfig == null) {
                break;
            }
            var task = new Consumer(newTaskConfig);
            pool.execute(task);
            logger.info("task added: {}", task.getName());
        }
        while (pool.getActiveCount() > 0) {
            try {
                logger.info("Active tasks: {}", pool.getActiveCount());
                Thread.sleep(500);
                continue;
            } catch (InterruptedException e) {
                continue;
            }
        }
        logger.info("shutdown pool");
        pool.shutdown();
    }
}

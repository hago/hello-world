/*
 * Copyright (c) 2020.
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.sbweb.controller.queuedapi;

import com.hagoapp.poc.AppLogger;
import org.slf4j.Logger;

import java.util.Map;
import java.util.concurrent.*;

public class ApiQueue {

    private static final Logger logger = AppLogger.getLogger();

    private static class ExecutorPerIdentity {
        private final String identity;
        private final BlockingQueue<ApiRunner<?>> taskQueue = new SynchronousQueue<>();
        private final Thread executor = new Thread(() -> {
            while (true) {
                try {
                    var task = taskQueue.take();
                    logger.info("task is found from queue of executor {}", this);
                    task.start();
                    task.join();
                } catch (InterruptedException e) {
                    break;
                }
            }
        });

        public void addTask(ApiRunner<?> runner) {
            logger.info("add runner {}", runner.getName());
            taskQueue.add(runner);
        }

        public ExecutorPerIdentity(String id) {
            identity = id;
        }

        @Override
        public String toString() {
            return "ExecutorPerIdentity{" +
                    "identity='" + identity + '\'' +
                    '}';
        }
    }

    private static final Map<String, ExecutorPerIdentity> apiQueueMap = new ConcurrentHashMap<>();

    public static void addTask(ApiRunner<?> runner) {
        var executor = apiQueueMap.compute(runner.getQueueIdentity(), (key, existed) -> {
            if (existed == null) {
                logger.warn("executor for {} not existed, creating", key);
                return new ExecutorPerIdentity(key);
            } else {
                logger.warn("executor for {} found existing", key);
                return existed;
            }
        });
        executor.addTask(runner);
    }

}

/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe;

import com.hagoapp.poc.AppLogger;
import org.reflections.Reflections;
import org.reflections.scanners.Scanners;
import org.slf4j.Logger;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;

public class ConsumerFactory {
    private static final Map<String, Class<? extends ConsumerConfig>> configMap = new HashMap<>();
    private static final Map<String, Class<? extends Consumer>> consumerMap = new HashMap<>();
    private static final Logger logger = AppLogger.getLogger();

    static {
        registerConsumers(ConsumerFactory.class.getPackageName());
    }

    public static void registerConsumers(String packageName) {
        var r = new Reflections(packageName, Scanners.SubTypes);
        for (var clz : r.getSubTypesOf(ConsumerConfig.class)) {
            try {
                var constructor = clz.getConstructor();
                var instance = constructor.newInstance();
                var name = instance.getConsumerType();
                if (configMap.containsKey(name)) {
                    logger.warn("Conflict: config nme {} of {} is replaced y {}", name,
                            configMap.get(name).getCanonicalName(), clz.getCanonicalName());
                }
                configMap.put(name, clz);
            } catch (InvocationTargetException | NoSuchMethodException | InstantiationException |
                     IllegalAccessException e) {
                logger.error("{} is not a valid config", clz.getCanonicalName());
            }
        }
        for (var clz : r.getSubTypesOf(Consumer.class)) {
            try {
                var constructor = clz.getConstructor();
                var instance = constructor.newInstance();
                var name = instance.supportConsumerType();
                if (consumerMap.containsKey(name)) {
                    logger.warn("Conflict: consumer nme {} of {} is replaced y {}", name,
                            configMap.get(name).getCanonicalName(), clz.getCanonicalName());
                }
                consumerMap.put(name, clz);
            } catch (InvocationTargetException | NoSuchMethodException | InstantiationException |
                     IllegalAccessException e) {
                logger.error("{} is not a valid config", clz.getCanonicalName());
            }
        }
    }

    public static Consumer createConsumer(ConsumerConfig config) {
        var clz = consumerMap.get(config.getConsumerType());
        if (clz == null) {
            logger.error("consumer type {} is not supported", config.getConsumerType());
            throw new UnsupportedOperationException(
                    String.format("consumer type %s is not supported", config.getConsumerType()));
        }
        try {
            var constructor = clz.getConstructor();
            var instance = constructor.newInstance();
            instance.loadConfig(config);
            return instance;
        } catch (InvocationTargetException | NoSuchMethodException | InstantiationException |
                 IllegalAccessException e) {
            logger.error("error {} while instantiate {}", e.getMessage(), clz.getCanonicalName());
            throw new UnsupportedOperationException(
                    String.format("error %s while instantiate %s", e.getMessage(), clz.getCanonicalName()));
        }
    }
}

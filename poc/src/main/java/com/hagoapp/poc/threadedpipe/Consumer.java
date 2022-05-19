/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe;

import com.hagoapp.poc.AppLogger;
import org.slf4j.Logger;

import java.io.Closeable;
import java.io.IOException;

public abstract class Consumer implements Runnable, Closeable {

    protected final Logger logger = AppLogger.getLogger();
    public abstract void loadConfig(ConsumerConfig config);

    public abstract String supportConsumerType();

    public abstract String getName();

    @Override
    public void close() throws IOException {
        // do nothing by default
    }
}

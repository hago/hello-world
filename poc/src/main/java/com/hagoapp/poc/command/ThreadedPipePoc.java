/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.command;

import com.hagoapp.poc.threadedpipe.ThreadedPipe;
import picocli.CommandLine.*;

import java.io.IOException;

@Command(name = "tpool")
public class ThreadedPipePoc extends CommandWithConfig {

    @Option(names = {"-min", "--minimum"}, defaultValue = "5")
    private int minThreadCount;
    @Option(names = {"-max", "--maximum"}, defaultValue = "20")
    private int maxThreadCount;

    @Override
    public Integer call() throws IOException {
        super.call();
        ThreadedPipe.run(minThreadCount, maxThreadCount);
        return 0;
    }
}

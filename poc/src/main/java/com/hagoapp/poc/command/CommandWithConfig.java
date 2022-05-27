/*
 * Copyright (c) 2020.
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 *
 */

package com.hagoapp.poc.command;

import com.fasterxml.jackson.jr.ob.JSON;
import com.hagoapp.poc.AppLogger;
import org.slf4j.Logger;
import picocli.CommandLine;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Callable;

@CommandLine.Command
public class CommandWithConfig implements Callable<Integer> {
    @CommandLine.Option(names = {"-c", "--config"}, description = "specify config file, ./config.json by default ")
    protected String configFile = "config.json";
    protected Map<String, Object> configuration = new HashMap<>();
    protected Logger logger = AppLogger.getLogger();

    @Override
    public Integer call() throws IOException {
        if ((this.configFile == null) || this.configFile.isBlank()) {
            throw new UnsupportedOperationException("config file not provided");
        }
        if (!new File(configFile).exists()) {
            throw new UnsupportedOperationException(String.format("config file %s not found", configFile));
        }
        try (var fis = new FileInputStream(configFile)) {
            var bytes = fis.readAllBytes();
            var json = new String(bytes, StandardCharsets.UTF_8);
            configuration = JSON.std.mapFrom(json);
        }
        return 0;
    }

    public Map<String, Object> getConfiguration() {
        return configuration;
    }
}

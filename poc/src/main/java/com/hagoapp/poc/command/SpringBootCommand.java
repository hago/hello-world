/*
 * Copyright (c) 2020.
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.command;

import com.hagoapp.poc.sbweb.WebApplication;
import picocli.CommandLine;

import java.io.IOException;

@CommandLine.Command(name = "sbweb")
public class SpringBootCommand extends CommandWithConfig {
    @Override
    public Integer call() throws IOException {
        super.call();
        WebApplication.run();
        return 0;
    }


}

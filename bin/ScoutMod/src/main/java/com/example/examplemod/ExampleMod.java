package com.example.examplemod;

import net.minecraftforge.common.MinecraftForge;

import net.minecraft.init.Blocks;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.Mod.EventHandler;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;


@Mod(modid = ExampleMod.MODID, version = ExampleMod.VERSION)
public class ExampleMod
{
    public static final String MODID = "examplemod";
    public static final String VERSION = "1.0";
    
    @EventHandler
    public void init(FMLInitializationEvent event)
    {
        // some example code

        MinecraftForge.EVENT_BUS.register(new EventEntityJoinWorld());
        MinecraftForge.EVENT_BUS.register(new EventServerChat());
    }
}

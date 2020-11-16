package com.example.examplemod;

import net.minecraft.entity.entity;
import net.minecraft.entity.ai.EntityAIBase;
import net.minecraft.entity.ai.EntityAIFollowOwner;
import net.minecraft.entity.ai.EntityAITasks.EntityAITaskEntry;
import net.minecraft.entity.passive.EntityWolf; // (https://skmedix.github.io/ForgeJavaDocs/javadoc/forge/1.9.4-12.17.0.2051/net/minecraft/entity/passive/EntityWolf.html)
import net.minecraftforge.event.entity.EntityJoinWorldEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraft.world.World; 

import net.minecraft.entity.player.EntityPlayer;



public class WolfCommands {

    public static EntityWolf getSpecificWolf(String name, World world) {
        return null;
    }

    public static void removeAllTasks(EntityWolf wolf) {
        for (Object a : pupper.tasks.taskEntries.toArray()) {
                EntityAIBase task = ((EntityAITaskEntry) a).action;           
                System.out.format("Removed task from wolf\n");
                pupper.tasks.removeTask(task);
            }
    }

    public static boolean followPlayer(EntityWolf wolf) {
        System.out.format("[COMMAND] followPlayer executing\n");
        WolfCommands.removeAllTasks(wolf);
        wolf.tasks.addTask(0, EntityAIFollowOwner(wolf );
        

    }
}